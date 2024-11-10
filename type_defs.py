from typing import NamedTuple

Time = float
Id = int


class Coordinates(NamedTuple):
    """
    x: float \n
    y: float
    """

    x: float
    y: float


class Circle(NamedTuple):
    """
    center: Coordinates \n
    radius: float
    """

    center: Coordinates
    radius: float


class SnapshotDetails(NamedTuple):
    """
    pos: Coordinates \n
    state: float \n
    frozen: bool \n
    terminated: bool \n
    """

    pos: Coordinates
    state: str
    frozen: bool
    terminated: bool


class Event(NamedTuple):
    """
    id: int \n
    state: str \n
    time: float | Time
    """

    id: int
    state: str
    time: float


class PriorityEvent(NamedTuple):
    """
    priority: float \n
    Event: Event
    """

    priority: float
    Event: Event


class Orientation(NamedTuple):
    """
    translation = float \n
    rotation = float \n
    reflection = float
    """

    translation = float
    rotation = float
    reflection = float
