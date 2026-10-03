from enum import Enum

class TypingState(Enum):
    ARUCO_ALIGN = 1
    DISTANCE_CHECK = 2
    XY_ALIGN = 3
    ALIGNED = 4