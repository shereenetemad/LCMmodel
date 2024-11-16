from enums import *
from type_defs import *
from robot import Robot
import numpy as np
import heapq
import math
import logging

logger = logging.getLogger(__name__)


class Scheduler:

    def __init__(
        self,
        seed: int,
        num_of_robots: int,
        initial_positions: list[float] | None,
        robot_speeds: float | list[float],
        algorithm: str = Algorithm.GATHERING,
        visibility_radius: float | list[float] | None = None,
        robot_orientations: list[Orientation] | None = None,
        robot_colors: list[str] | None = None,
        obstructed_visibility: bool = False,
        rigid_movement: bool = True,
        multiplicity_detection: bool = False,
        probability_distribution: str = DistributionType.GAUSSIAN,
        scheduler_type: str = SchedulerType.ASYNC,
        time_precision: int = 5,
        threshold_precision: int = 5,
        sampling_rate: float = 0.2,
        labmda_rate: float = 5,
    ):
        self.seed = seed
        self.terminate = False
        self.rigid_movement = rigid_movement
        self.multiplicity_detection = multiplicity_detection
        self.probability_distribution = probability_distribution
        self.scheduler_type = scheduler_type
        self.robot_speeds = robot_speeds
        self.visibility_radius = visibility_radius
        self.robot_orientations = robot_orientations
        self.robot_colors = robot_colors
        self.obstructed_visibility = obstructed_visibility
        self.time_precision = time_precision
        self.threshold_precision = threshold_precision
        self.snapshot_history: list[tuple[Time, dict[int, SnapshotDetails]]] = []
        self.visualization_snapshots: list[tuple[Time, dict[int, SnapshotDetails]]] = []
        self.sampling_rate = sampling_rate
        self.lambda_rate = labmda_rate  # Average number of events per time unit
        self.robots: list[Robot] = []

        if isinstance(robot_speeds, float) or isinstance(robot_speeds, int):
            robot_speeds_list = [robot_speeds] * num_of_robots

        for i in range(num_of_robots):
            new_robot = Robot(
                id=i,
                coordinates=Coordinates(*initial_positions[i]),
                threshold_precision=threshold_precision,
                speed=robot_speeds_list[i],
                algorithm=algorithm,
            )
            self.robots.append(new_robot)

        self.initialize_queue_exponential()

    def get_snapshot(
        self, time: float, visualization_snapshot: bool = False
    ) -> dict[int, SnapshotDetails]:
        snapshot = {}
        for robot in self.robots:
            snapshot[robot.id] = SnapshotDetails(
                robot.get_position(time),
                robot.state,
                robot.frozen,
                robot.terminated,
            )

        if visualization_snapshot:
            self.visualization_snapshots.append((time, snapshot))
        else:
            self.snapshot_history.append((time, snapshot))

        return snapshot

    def generate_event(self, current_event: Event) -> None:
        # Visualization events
        if current_event.state == None and len(self.priority_queue) > 0:
            new_event_time = current_event.time + self.sampling_rate
            priority_event = PriorityEvent(
                new_event_time,
                Event(-1, None, new_event_time),
            )
            heapq.heappush(self.priority_queue, priority_event)
            return

        new_event_time = 0.0
        robot = self.robots[current_event.id]

        # Robot will definitely reach calculated position
        if self.rigid_movement == True and current_event.state == RobotState.MOVE:
            new_event_time = current_event.time + (
                math.dist(robot.calculated_position, robot.start_position) / robot.speed
            )
        else:
            new_event_time = current_event.time + self.generator.exponential(
                scale=1 / self.lambda_rate
            )

        new_event_time = self._precise_time(new_event_time)
        new_event_state = robot.state.next_state()

        priority_event = PriorityEvent(
            new_event_time,
            Event(current_event.id, new_event_state, new_event_time),
        )

        heapq.heappush(self.priority_queue, priority_event)

    def handle_event(self) -> int:
        exit_code = -1

        if len(self.priority_queue) == 0:
            return exit_code

        current_event = heapq.heappop(self.priority_queue)[1]

        event_state = current_event.state
        robot = self.robots[current_event.id]
        time = self._precise_time(current_event.time)

        if event_state == RobotState.LOOK:
            robot.look(self.get_snapshot(time), time)

            # Removes robot from simulation
            if robot.terminated == True:
                return 4
            exit_code = 1
        elif event_state == RobotState.MOVE:
            robot.move(time)
            exit_code = 2
        elif event_state == RobotState.WAIT:
            robot.wait(time)
            exit_code = 3
        elif event_state == None:
            self.get_snapshot(time, visualization_snapshot=True)
            exit_code = 0

        self.generate_event(current_event)
        return exit_code

    def initialize_queue(self) -> None:
        # Set the lambda parameter (average rate of occurrences)
        lambda_value = 5  # 5 occurrences per interval

        # Generate Poisson-distributed random numbers
        generator = np.random.default_rng()
        num_samples = 2  # Total number of samples to generate
        poisson_numbers = generator.poisson(lambda_value, num_samples)

        # Display the generated numbers
        logger.info(poisson_numbers)

    def initialize_queue_exponential(self) -> None:
        logger.info(f"Seed used: {self.seed}")

        # Generate time intervals for n events
        self.generator = np.random.default_rng(seed=self.seed)
        num_of_events = len(self.robots)
        time_intervals = self.generator.exponential(
            scale=1 / self.lambda_rate, size=num_of_events
        ).round(self.time_precision)

        logger.info(
            f"Time precision: {self.time_precision} Time intervals between events: {time_intervals}"
        )

        initial_event = Event(-1, None, 0.0)  # initial event for visualization
        self.priority_queue: list[PriorityEvent] = [PriorityEvent(0.0, initial_event)]

        for robot in self.robots:
            time = self._precise_time(time_intervals[robot.id])
            event = Event(robot.id, robot.state.next_state(), time)
            self.priority_queue.append(PriorityEvent(time, event))

        heapq.heapify(self.priority_queue)

    def _all_robots_reached(self) -> bool:
        for robot in self.robots:
            if robot.frozen == False:
                return False
        return True

    def _precise_time(self, x: float) -> float:
        return round(x, self.time_precision)
