# Asynchronous Scheduler

A simulator for Look Compute Move robots in the Asynchronous System

## Installing required packages

`pip install -r requirements.txt`

## Running the Simulator

### Windows

`python run.py`

### MacOS / Linux

`python3 run.py`

The configuration takes the following variables.

- number of robots
- initial position (can be random) : list of points in 2D
- speed of robots : number or a list
- type of scheduler (default: async)
- probability distribution (default: gaussian)
- visibility radius : number or a list of floats
- orientation of robots: same or random (input as a list of triple(translation, rotation, reflection))
- multiplicity detection
- colors
- obstructed visibility
- rigidity

## Default Configuration

- Unlimited visibility
- No Multiplicity detection
- Ignore Collisions
- Transparent robots
- Rigid movement

## Files

- config.json
- scheduler.py
- robot.py
- run.py

## Functions

- Scheduler Functions:

  - get_snapshot(): Dict[int, Tuple[Tuple[float, float], str]]
  - generate_event(): None
  - handle_event(event: tuple[int, str, float]): None

- Robot Functions:
  - look(): None
  - compute(): None
  - move(): None
  - get_position(): tuple[float, float]
  - convert_coordinate(tuple[x: float, y: float]): tuple[float, float]

## Data Structures

- Snapshot: Dictionary of ID, Position, Color (optional)
- Priority Queue: Each element contains a 3-tuple containing
  - robot_id: int
  - state: str (either "look", "compute", "move")
  - time: float
