from robot_states import RobotStates

class Robot:
    def __init__(self, speed: float, color: str, visibility_radius: float, orientation: tuple(float, float, float), obstructed_visibility: bool, multiplicity_detection: bool, rigid_movement: bool):
        self.speed = speed
        self.color = color
        self.visibility_radius = visibility_radius
        self.obstructed_visibility = obstructed_visibility
        self.multiplicity_detection = multiplicity_detection
        self.rigid_movement = rigid_movement
        self.orientation = orientation
        self.start_time = None
        self.end_time = None
        self.current_time = None
        self.state = RobotStates.SLEEP
        self.calculated_position = None
        self.number_of_activations = 0
        self.travelled_distance = 0
        pass
        
    def look(self) -> None:
        pass
    
    def compute(self) -> None:
        pass
    
    def move(self) -> None:
        pass

    def get_position(self) -> tuple[float, float]:
        pass
    
    def convert_coordinate(self, coord: tuple[float, float]) -> tuple[float, float]:
        pass

        