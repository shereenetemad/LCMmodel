from enums import RobotState
from type_defs import *

class Robot:
    def __init__(self, id: int, speed: float | None = None, color: str | None = None, visibility_radius: float | None = None, orientation: tuple[float , float , float] | None = None, obstructed_visibility: bool = False, multiplicity_detection: bool = False, rigid_movement: bool = False, coordinates: Coordinates = None):
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
        self.state = RobotState.SLEEP
        self.calculated_position = None
        self.number_of_activations = 0
        self.travelled_distance = 0
        self.snapshot = None
        self.coordinates = coordinates
        self.id = id
        
    def look(self, snapshot: dict[Id, tuple[Coordinates,State]]) -> None:
        self.snapshot = {key: self.convert_coordinate(value) for key, value in snapshot.items() if self.robot_is_visible(value[0])}
        self.compute(self.midpoint)
        
    
    def compute(self, algo) -> Coordinates:
        coord = algo()
        return coord
    
    def move(self) -> None:
        pass

    def get_position(self, time: float) -> Coordinates:
        pass
    
    def convert_coordinate(self, coord: Coordinates) -> Coordinates:
        return coord

    def robot_is_visible(self, coord: Coordinates):
        return True
    
    def midpoint(self) -> Coordinates:
        x = y = 0
        for _, value in self.snapshot.items():
            x += value[0][0]
            y += value[0][1]
        
        x = x / len(self.snapshot)
        y = y / len(self.snapshot)
          
        return (x, y) 
        