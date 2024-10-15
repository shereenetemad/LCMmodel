from enum import Enum

class RobotState(Enum):
    LOOK = 0
    MOVE = 1
    WAIT = 2
    
    def next_state(self):
        if self == RobotState.LOOK:
            return RobotState.MOVE
        elif self == RobotState.MOVE:
            return RobotState.WAIT
        elif self == RobotState.WAIT:
            return RobotState.LOOK


class SchedulerType(Enum):
    ASYNC = "async"

class DistributionType(Enum):
    GAUSSIAN = "gaussian"