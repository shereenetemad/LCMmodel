type Snapshot = [
  number,
  Record<string, [Coordinates, State, FrozenState, TerminatedState]>
];

type RobotMap = Record<string, Robot>;

type Coordinates = [number, number];

type State = string;

type FrozenState = boolean;

type TerminatedState = boolean;

type QueueNode = { value: Snapshot; next: QueueNode | undefined };

type Circle = [Coordinates, number];
