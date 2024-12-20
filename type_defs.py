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

    def __str__(self):
        return f"({float(self.x)}, {float(self.y)})"


class Circle(NamedTuple):
    """
    center: Coordinates \n
    radius: float
    """

    center: Coordinates
    radius: float

    def __str__(self):
        return f"Center: {self.center} ; radius: {float(self.radius)}"


class SnapshotDetails(NamedTuple):
    """
    pos: Coordinates \n
    state: float \n
    frozen: bool \n
    terminated: bool \n
    multiplicity: int | None
    """

    pos: Coordinates
    state: str
    frozen: bool
    terminated: bool
    multiplicity: int | None


class Event(NamedTuple):
    """
    time: float | Time \n
    id: int \n
    state: str
    """

    time: float
    id: int
    state: str


class Orientation(NamedTuple):
    """
    translation = float \n
    rotation = float \n
    reflection = float
    """

    translation = float
    rotation = float
    reflection = float
