from enum import Enum


class RobotState(str, Enum):
    LOOK = "LOOK"
    MOVE = "MOVE"
    WAIT = "WAIT"

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
