from enum import Enum

class RobotState(Enum):
    LOOK = "Look"
    MOVE_START = "Move start"
    MOVE_END = "Move end"
    SLEEP = "Sleep"
