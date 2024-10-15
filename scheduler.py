from enums import SchedulerType, DistributionType
from type_defs import *
from robot import Robot
import numpy as np
import heapq

class Scheduler:
    
    def __init__(self, num_of_robots: int, initial_positions: list[float] | None, robot_speeds: float | list[float], visibility_radius: float | list[float] | None = None, robot_orientations: list[tuple[Translation, Rotation, Reflection]] | None = None,  robot_colors: list[str] | None = None, obstructed_visibility: bool = False, rigid_movement: bool = True, multiplicity_detection: bool = False, probability_distribution: str = DistributionType.GAUSSIAN, scheduler_type: str =SchedulerType.ASYNC): 
        
        
        self.robots: list[Robot] = []
        for i in range(num_of_robots):
            new_robot = Robot(id = i)
            self.robots.append(new_robot)
            
        self.initialize_queue_exponential()
    
    def get_snapshot(self) -> dict[int, tuple[Coordinates,str]]:
        snapshot = {}
        for robot in self.robots:
            snapshot[robot.id] = (robot.get_position(), robot.color)

        return snapshot

    def generate_event(self) -> None:
        pass
    
    def handle_event(self, event: tuple[int, str, float]) -> None:
        pass

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
        lambda_rate = 5  # Average number of events per time unit
        
        # Generate a random number
        seed = np.random.default_rng().integers(0, 2**32 - 1)  # Random integer in the range of 0 to 2^32-1

        # Generate time intervals for n events
        generator = np.random.default_rng(seed = seed)
        n_events = len(self.robots)
        time_intervals = generator.exponential(scale=1/ lambda_rate, size=n_events)

        print("Time intervals between events:", time_intervals)
        
        self.priority_queue: list[tuple[Priority, tuple[Id, State, Time]]] = []
        
        for robot in self.robots:
            time = time_intervals[robot.id]
            item = (robot.id, robot.state, time)
            self.priority_queue.append((time, item))
            
        heapq.heapify(self.priority_queue)
        