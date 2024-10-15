from enums import *
from type_defs import *
from robot import Robot
import numpy as np
import heapq

class Scheduler:
    
    def __init__(self, num_of_robots: int, initial_positions: list[float] | None, robot_speeds: float | list[float], visibility_radius: float | list[float] | None = None, robot_orientations: list[tuple[Translation, Rotation, Reflection]] | None = None,  robot_colors: list[str] | None = None, obstructed_visibility: bool = False, rigid_movement: bool = True, multiplicity_detection: bool = False, probability_distribution: str = DistributionType.GAUSSIAN, scheduler_type: str =SchedulerType.ASYNC): 
        
        
        self.robots: list[Robot] = []
        for i in range(num_of_robots):
            new_robot = Robot(id = i, coordinates=tuple(initial_positions[i]))
            self.robots.append(new_robot)
            
        self.initialize_queue_exponential()
    
    def get_snapshot(self, time: float) -> dict[int, tuple[Coordinates,str]]:
        snapshot = {}
        for robot in self.robots:
            snapshot[robot.id] = (robot.get_position(time), robot.color)

        return snapshot

    def generate_event(self, current_event: tuple[Id, RobotState, Time]) -> None:
        new_event_time = current_event[2] + self.generator.exponential(scale=1/ self.lambda_rate)
        new_event = (new_event_time, (current_event[0], current_event[1].next_state(), new_event_time))
        
        heapq.heappush(self.priority_queue, new_event)
    
    def handle_event(self) -> None:
        
        next_event = heapq.heappop(self.priority_queue)[1]
        self.generate_event(next_event)
        
        next_state = next_event[1]
        robot = self.robots[next_event[0]]
        time = next_event[2]
        
        if next_state == RobotState.LOOK:
            robot.state = RobotState.LOOK
            robot.look(self.get_snapshot(time))
        elif next_state == RobotState.MOVE:
            robot.state = RobotState.MOVE
            robot.move(time)
        elif next_state == RobotState.WAIT:
            robot.state = RobotState.WAIT
            robot.wait(time)

    def initialize_queue(self) -> None:
        # Set the lambda parameter (average rate of occurrences)
        lambda_value = 5  # 5 occurrences per interval

        
        # Generate Poisson-distributed random numbers
        generator = np.random.default_rng()
        num_samples = 2  # Total number of samples to generate
        poisson_numbers = generator.poisson(lambda_value, num_samples)

        # Display the generated numbers
        print(poisson_numbers)
        
        
    def initialize_queue_exponential(self) -> None:
        # Set the rate parameter (lambda)
        self.lambda_rate = 5  # Average number of events per time unit
        
        # Generate a random number
        self.generator_seed = np.random.default_rng().integers(0, 2**32 - 1)

        # Generate time intervals for n events
        self.generator = np.random.default_rng(seed = self.generator_seed)
        num_of_events = len(self.robots)
        time_intervals = self.generator.exponential(scale=1/ self.lambda_rate, size=num_of_events)

        print("Time intervals between events:", time_intervals)
        
        self.priority_queue: list[tuple[Priority, tuple[Id, RobotState, Time]]] = []
        
        for robot in self.robots:
            time = time_intervals[robot.id]
            item = (robot.id, robot.state.next_state(), time)
            self.priority_queue.append((time, item))
            
        heapq.heapify(self.priority_queue)
        