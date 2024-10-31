from enums import RobotState
from type_defs import *
import math
import logging

logger = logging.getLogger(__name__)


class Robot:
    def __init__(
        self,
        id: int,
        speed: float = 1.0,
        color: str | None = None,
        visibility_radius: float | None = None,
        orientation: tuple[float, float, float] | None = None,
        obstructed_visibility: bool = False,
        multiplicity_detection: bool = False,
        rigid_movement: bool = False,
        coordinates: Coordinates = None,
    ):
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
        self.state = RobotState.WAIT
        self.start_position = coordinates
        self.calculated_position = None
        self.number_of_activations = 0
        self.travelled_distance = 0.0
        self.snapshot: dict[Id, tuple[Coordinates, State]] = None
        self.coordinates = coordinates
        self.id = id

    def look(self, snapshot: dict[Id, tuple[Coordinates, State]], time: float) -> None:
        self.snapshot = {
            key: self._convert_coordinate(value)
            for key, value in snapshot.items()
            if self._robot_is_visible(value[0])
        }
        logger.info(f"[{time:.6f}] {{R{self.id}}} LOOK    -- Snapshot {self.snapshot}")

        self.calculated_position = self._compute(self._midpoint)
        sec = self._smallest_enclosing_circle()
        pos_str = f"({float(self.calculated_position[0]):.6f}, {float(self.calculated_position[1]):.6f})"
        logger.info(f"[{time:.6f}] {{R{self.id}}} COMPUTE -- Computed Pos: {pos_str}")
        logger.info(f"[{time:.6f}] {{R{self.id}}} COMPUTE -- Computed SEC: {sec}")

    def _compute(self, algo) -> Coordinates:
        coord = algo()
        return coord

    def move(self, start_time: float) -> None:
        logger.info(f"[{start_time:.6f}] {{R{self.id}}} MOVE")

        self.start_time = start_time

    def wait(self, time: float) -> None:
        self.end_time = time

        self.coordinates = self.get_position(time)
        self.travelled_distance += math.dist(self.start_position, self.coordinates)

        self.start_position = self.coordinates
        logger.info(
            f"[{time:.6f}] {{R{self.id}}} WAIT    -- Travelled a total of {self.travelled_distance} units"
        )

        self.calculated_position = None
        self.start_time = None
        self.end_time = None

    def get_position(self, time: float) -> Coordinates:
        self.current_time = time

        if self.calculated_position == None:
            return self.coordinates

        distance = math.dist(self.start_position, self.calculated_position)
        distance_covered = self.speed * time

        if distance_covered > distance:
            self.coordinates = self.calculated_position
        else:
            factor = distance_covered / distance
            self.coordinates = self._interpolate(
                self.start_position, self.calculated_position, factor
            )

        return self.coordinates

    def _interpolate(
        self, start: Coordinates, end: Coordinates, t: float
    ) -> Coordinates:
        return (start[0] + t * (end[0] - start[0]), start[1] + t * (end[1] - start[1]))

    def _convert_coordinate(self, coord: Coordinates) -> Coordinates:
        return coord

    def _robot_is_visible(self, coord: Coordinates):
        return True

    def _midpoint(self) -> Coordinates:
        x = y = 0
        for _, value in self.snapshot.items():
            x += value[0][0]
            y += value[0][1]

        x = x / len(self.snapshot)
        y = y / len(self.snapshot)

        return (x, y)

    def _smallest_enclosing_circle(self) -> Coordinates:
        num_robots = len(self.snapshot)
        destination: Coordinates | None = None
        if num_robots == 0:
            destination = (0, 0)
        if num_robots == 1:
            destination = self.snapshot[0][0]
        else:
            sec: Circle = self._sec(num_robots)
            destination = self._closest_point_on_circle(sec, self.coordinates)

        return destination

    def _sec(self, num_robots: int) -> Circle:
        """Returns smallest enclosing circle given number of robots in the form of
        (Center, Radius)"""

        sec: Circle = ((0, 0), 10**18)
        for i in range(num_robots):
            for j in range(i + 1, num_robots):
                a = self.snapshot[i][0]
                b = self.snapshot[j][0]
                circle = self._circle_from_two(a, b)
                radius1 = circle[1]
                radius2 = sec[1]
                if radius1 < radius2 and self._valid_circle(circle):
                    sec = circle

        for i in range(num_robots):
            for j in range(i + 1, num_robots):
                for k in range(j + 1, num_robots):
                    a = self.snapshot[i][0]
                    b = self.snapshot[j][0]
                    c = self.snapshot[k][0]
                    circle = self._circle_from_three(a, b, c)
                    radius1 = circle[1]
                    radius2 = sec[1]
                    if radius1 < radius2 and self._valid_circle(circle):
                        sec = circle
        return sec

    def _closest_point_on_circle(
        self, circle: Circle, point: Coordinates
    ) -> Coordinates:

        # Vector from the center of the circle to the point
        center: Coordinates = circle[0]
        radius: float = circle[1]
        vx, vy = point[0] - center[0], point[1] - center[1]

        # Distance from the center to the point
        d = self._distance(center, point)

        # Scaling factor to project the point onto the circle
        scale = radius / d

        # Closest point on the circle
        cx = center[0] + vx * scale
        cy = center[1] + vy * scale

        return (cx, cy)

    def _valid_circle(self, circle: Circle) -> bool:
        """Returns False if at least one point does not lie within given circle"""

        # Iterate through all coordinates
        for _, coord in self.snapshot.items():
            # If point does not lie inside of the given circle; i.e.: if
            # distance between the center coord and point is more than radius
            if self._distance(circle[0], coord[0]) > circle[1]:
                return False
        return True

    def _circle_from_two(self, a: Coordinates, b: Coordinates) -> Circle:
        """Returns circle intersecting two points"""

        # Midpoint between a and b
        center = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
        return (center, self._distance(a, b) / 2.0)

    def _circle_from_three(
        self, a: Coordinates, b: Coordinates, c: Coordinates
    ) -> Circle:
        """Returns circle intersecting three points"""

        center = self._circle_center(b[0] - a[0], b[1] - a[1], c[0] - a[0], c[1] - a[1])
        center[0] += a[0]
        center[1] += a[1]
        return (center, self._distance(center, a))

    def _circle_center(self, bx: float, by: float, cx: float, cy: float) -> Coordinates:
        b = bx * bx + by * by
        c = cx * cx + cy * cy
        d = bx * cy - by * cx
        if d == 0:
            return (0, 0)
        return ((cy * b - by * c) // (2 * d), (bx * c - cx * b) // (2 * d))

    def _distance(self, a: Coordinates, b: Coordinates) -> float:
        return math.sqrt(pow(a[0] - b[0], 2) + pow(a[1] - b[1], 2))

    def __str__(self):
        return f"R{self.id}, speed: {self.speed}, color: {self.color}, coordinates: {self.coordinates}"
