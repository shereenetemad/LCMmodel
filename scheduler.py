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
        num_of_robots: int,
        initial_positions: list[float] | None,
        robot_speeds: float | list[float],
        visibility_radius: float | list[float] | None = None,
        robot_orientations: (
            list[tuple[Translation, Rotation, Reflection]] | None
        ) = None,
        robot_colors: list[str] | None = None,
        obstructed_visibility: bool = False,
        rigid_movement: bool = True,
        multiplicity_detection: bool = False,
        probability_distribution: str = DistributionType.GAUSSIAN,
        scheduler_type: str = SchedulerType.ASYNC,
    ):
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
        self.snapshot_history: list[tuple[Time, dict[int, tuple[Coordinates, str]]]] = (
            []
        )
        self.robots: list[Robot] = []
        for i in range(num_of_robots):
            new_robot = Robot(id=i, coordinates=tuple(initial_positions[i]))
            self.robots.append(new_robot)

        self.initialize_queue_exponential()

    def get_snapshot(self, time: float) -> dict[int, tuple[Coordinates, str]]:
        snapshot = {}
        for robot in self.robots:
            snapshot[robot.id] = (robot.get_position(time), robot.state)

        self.snapshot_history.append((time, snapshot))
        if self.unchanged_history(15) == True:
            self.terminate = True
        return snapshot

    def generate_event(self, current_event: tuple[Id, RobotState, Time]) -> None:
        new_event_time = 0.0

        if self.rigid_movement == True and current_event[1] == RobotState.MOVE:
            robot = self.robots[current_event[0]]
            new_event_time = current_event[2] + (
                math.dist(robot.calculated_position, robot.start_position) / robot.speed
            )
        else:
            new_event_time = current_event[2] + self.generator.exponential(
                scale=1 / self.lambda_rate
            )

        new_event = (
            new_event_time,
            (current_event[0], current_event[1].next_state(), new_event_time),
        )

        heapq.heappush(self.priority_queue, new_event)

    def handle_event(self) -> bool:
        if self.terminate == True:
            return False

        next_event = heapq.heappop(self.priority_queue)[1]

        next_state = next_event[1]
        robot = self.robots[next_event[0]]
        time = next_event[2]

        if next_state == RobotState.LOOK:
            robot.state = RobotState.LOOK
            robot.look(self.get_snapshot(time), time)
        elif next_state == RobotState.MOVE:
            robot.state = RobotState.MOVE
            robot.move(time)
        elif next_state == RobotState.WAIT:
            robot.state = RobotState.WAIT
            robot.wait(time)

        self.generate_event(next_event)
        return True

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
        # Set the rate parameter (lambda)
        self.lambda_rate = 5  # Average number of events per time unit

        # Generate a random number
        self.generator_seed = np.random.default_rng().integers(0, 2**32 - 1)
        logger.info(f"Seed used: {self.generator_seed}")

        # Generate time intervals for n events
        self.generator = np.random.default_rng(seed=self.generator_seed)
        num_of_events = len(self.robots)
        time_intervals = self.generator.exponential(
            scale=1 / self.lambda_rate, size=num_of_events
        )

        logger.info(f"Time intervals between events: {time_intervals}")

        self.priority_queue: list[tuple[Priority, tuple[Id, RobotState, Time]]] = []

        for robot in self.robots:
            time = time_intervals[robot.id]
            item = (robot.id, robot.state.next_state(), time)
            self.priority_queue.append((time, item))

        heapq.heapify(self.priority_queue)

    def unchanged_history(self, max_history) -> bool:
        length = len(self.snapshot_history)
        if length <= 1:
            return False

        count = max_history
        for i in range(length - 1, 0, -1):
            if count == 0:
                return True

            for robot_id in range(len(self.robots)):
                if (
                    self.snapshot_history[i][1][robot_id][0]
                    != self.snapshot_history[i - 1][1][robot_id][0]
                ):
                    return False

            count -= 1

        return count <= 0
