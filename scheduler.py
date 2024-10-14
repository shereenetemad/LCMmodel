from enums import SchedulerType, DistributionType
class Scheduler:
    
    def __init__(self, num_of_robots: int, initial_positions: float | None, robot_speeds: float | list[float], visibility_radius: float | list[float], robot_orientations: list[tuple[float, float, float]] | None, multiplicity_detection: bool, robot_colors: list[str] | None, obstructed_visibility: bool, rigid_movement: bool,probability_distribution: str = DistributionType.GAUSSIAN, scheduler_type: str =SchedulerType.ASYNC): 
        pass
        
    def get_snapshot(self) -> dict[int, tuple[tuple[float,float],str]]:
        pass

    def generate_event(self) -> None:
        pass
    
    def handle_event(self, event: tuple[int, str, float]) -> None:
        pass

        