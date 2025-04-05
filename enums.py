from enum import Enum

class RobotState(str, Enum):
    LOOK = "LOOK"
    MOVE = "MOVE"
    WAIT = "WAIT"
    TERMINATED = "TERMINATED"

    def next_state(self):
        if self == RobotState.LOOK:
            return RobotState.MOVE
        elif self == RobotState.MOVE:
            return RobotState.WAIT
        elif self == RobotState.WAIT:
            return RobotState.LOOK

class SchedulerType(Enum):
    ASYNC = "Async"

class DistributionType(Enum):
    EXPONENTIAL = "Exponential"

class Algorithm(Enum):
    GATHERING = "Gathering"
    SEC = "SEC"

# ===== NEW ADDITIONS BELOW =====
class FaultType(Enum):
    NONE = "No Fault"
    CRASH = "Crash (Instant Termination)"
    DELAY = "Delay (50% Speed)"
    WRONG_COMPUTE = "Wrong Computation"
    VISIBILITY = "Partial Visibility"
    MOVEMENT = "Inverted Movement"

class FaultStatus(Enum):
    INACTIVE = "Inactive"
    ACTIVE = "Active"
    TRIGGERED = "Triggered"
    RESOLVED = "Resolved"

# Verify nothing was removed by checking original classes
assert hasattr(RobotState, 'LOOK') 
assert hasattr(SchedulerType, 'ASYNC')
assert hasattr(DistributionType, 'EXPONENTIAL') 
assert hasattr(Algorithm, 'GATHERING')
