from enums import RobotState
from type_defs import *
import math
import logging

logger = logging.getLogger(__name__)


class Robot:
    def __init__(
        self,
        id: int,
        coordinates: Coordinates,
        speed: float = 1.0,
        color: str | None = None,
        visibility_radius: float | None = None,
        orientation: Orientation | None = None,
        obstructed_visibility: bool = False,
        multiplicity_detection: bool = False,
        rigid_movement: bool = False,
        threshold_precision: float = 5,
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
        self.snapshot: dict[Id, SnapshotDetails] | None = None
        self.coordinates = coordinates
        self.id = id
        self.threshold_precision = threshold_precision
        self.frozen = False  # true if we skipped move step
        self.terminated = False

    def look(
        self,
        snapshot: dict[Id, SnapshotDetails],
        time: float,
    ) -> None:
        self.state = RobotState.LOOK

        self.snapshot = {}
        for key, value in snapshot.items():
            if self._robot_is_visible(value.pos):
                transformed_pos = self._convert_coordinate(value.pos)
                self.snapshot[key] = SnapshotDetails(
                    transformed_pos, value.state, value.frozen, value.terminated
                )

        logger.info(
            f"[{time}] {{R{self.id}}} LOOK    -- Snapshot {self.prettify_snapshot(snapshot)}"
        )

        self.calculated_position = self._compute(
            self._midpoint, self._midpoint_terminal
        )

        pos_str = f"({self.calculated_position[0]}, {self.calculated_position[1]})"
        logger.info(f"[{time}] {{R{self.id}}} COMPUTE -- Computed Pos: {pos_str}")

        if self._distance(self.calculated_position, self.coordinates) < math.pow(
            10, -self.threshold_precision
        ):
            self.frozen = True
            self.wait(time)
        else:
            self.frozen = False

        # sec = self._smallest_enclosing_circle()
        # pos_str = f"({float(self.calculated_position[0]):.6f}, {float(self.calculated_position[1]):.6f})"
        # logger.info(f"[{time:.6f}] {{R{self.id}}} COMPUTE -- Computed Pos: {pos_str}")
        # logger.info(f"[{time:.6f}] {{R{self.id}}} COMPUTE -- Computed SEC: {sec}")

    def _compute(self, algo, check_terminal) -> Coordinates:
        coord = algo()

        if check_terminal(coord) == True:
            self.terminated = True

        return coord

    def move(self, start_time: float) -> None:
        self.state = RobotState.MOVE

        logger.info(f"[{start_time}] {{R{self.id}}} MOVE")

        self.start_time = start_time

    def wait(self, time: float) -> None:
        self.state = RobotState.WAIT

        self.end_time = time

        self.coordinates = self.get_position(time)
        current_distance = math.dist(self.start_position, self.coordinates)
        self.travelled_distance += current_distance

        self.start_position = self.coordinates
        logger.info(
            f"[{time}] {{R{self.id}}} WAIT    -- Distance: {current_distance} | Total Distance: {self.travelled_distance} units"
        )

        self.start_time = None
        self.end_time = None

    def get_position(self, time: float) -> Coordinates:
        self.current_time = time

        if self.state == RobotState.WAIT:
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
        return Coordinates(
            start.x + t * (end.x - start.x), start.y + t * (end.y - start.y)
        )

    def _convert_coordinate(self, coord: Coordinates) -> Coordinates:
        return coord

    def _robot_is_visible(self, coord: Coordinates):
        return True

    def _midpoint(self) -> Coordinates:
        x = y = 0
        for _, value in self.snapshot.items():
            x += value.pos.x
            y += value.pos.y

        x = x / len(self.snapshot)
        y = y / len(self.snapshot)

        return Coordinates(x, y)

    def _midpoint_terminal(self, coord) -> bool:
        num_robots = len(self.snapshot.keys())
        for i in range(num_robots - 1):
            if self._distance(self.snapshot[i].pos, coord) > math.pow(
                10, -self.threshold_precision
            ):
                return False
        return True

    def _smallest_enclosing_circle(self) -> Coordinates:
        num_robots = len(self.snapshot)
        destination: Coordinates | None = None
        if num_robots == 0:
            destination = (0, 0)
        if num_robots == 1:
            destination = self.snapshot[0].pos
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
                a = self.snapshot[i].pos
                b = self.snapshot[j].pos
                circle = self._circle_from_two(a, b)
                radius1 = circle[1]
                radius2 = sec[1]
                if radius1 < radius2 and self._valid_circle(circle):
                    sec = circle

        for i in range(num_robots):
            for j in range(i + 1, num_robots):
                for k in range(j + 1, num_robots):
                    a = self.snapshot[i].pos
                    b = self.snapshot[j].pos
                    c = self.snapshot[k].pos
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
        center: Coordinates = circle.center
        radius: float = circle.radius
        vx, vy = point.x - center.x, point.y - center.y

        # Distance from the center to the point
        d = self._distance(center, point)

        # Scaling factor to project the point onto the circle
        scale = radius / d

        # Closest point on the circle
        cx = center.x + vx * scale
        cy = center.y + vy * scale

        return Coordinates(cx, cy)

    def _valid_circle(self, circle: Circle) -> bool:
        """Returns False if at least one point does not lie within given circle"""

        # Iterate through all coordinates
        for _, coord in self.snapshot.items():
            # If point does not lie inside of the given circle; i.e.: if
            # distance between the center coord and point is more than radius
            if self._distance(circle.center, coord[0]) > circle.radius:
                return False
        return True

    def _circle_from_two(self, a: Coordinates, b: Coordinates) -> Circle:
        """Returns circle intersecting two points"""

        # Midpoint between a and b
        center = Coordinates((a.x + b.x) / 2.0, (a.y + b.y) / 2.0)
        return Circle(center, self._distance(a, b) / 2.0)

    def _circle_from_three(
        self, a: Coordinates, b: Coordinates, c: Coordinates
    ) -> Circle:
        """Returns circle intersecting three points"""

        center = self._circle_center(b.x - a.x, b.y - a.y, c.x - a.x, c.y - a.y)

        translated_center = Coordinates(center.x + a.x, center.y + a.y)

        return Circle(translated_center, self._distance(center, a))

    def _circle_center(self, bx: float, by: float, cx: float, cy: float) -> Coordinates:
        b = bx * bx + by * by
        c = cx * cx + cy * cy
        d = bx * cy - by * cx
        if d == 0:
            return Coordinates(0, 0)
        return Coordinates((cy * b - by * c) // (2 * d), (bx * c - cx * b) // (2 * d))

    def _distance(self, a: Coordinates, b: Coordinates) -> float:
        distance = math.dist(a, b)

        return distance

    def __str__(self):
        return f"R{self.id}, speed: {self.speed}, color: {self.color}, coordinates: {self.coordinates}"

    def prettify_snapshot(self, snapshot: dict[Id, SnapshotDetails]) -> str:
        result = ""
        for key, value in snapshot.items():
            frozen = "*" if value.frozen == True else ""
            terminated = "#" if value.frozen == True else ""
            result += f"\n\t{key}{frozen}{terminated}: {value[1]} - ({float(value.pos.x),float(value.pos.y)})"

        return result
