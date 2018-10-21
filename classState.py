from enum import Enum


class State(Enum):
    accepted = 1
    pendingLow = 2
    pendingHigh = 3
    rejeted = 4
