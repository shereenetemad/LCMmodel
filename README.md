# Asynchronous Scheduler

A simulator for Look-Compute-Move robots in the Asynchronous System

## Installing required packages

`pip install -r requirements.txt`

## Running the Simulator

### Windows

`python run.py`

### MacOS / Linux

`python3 run.py`

The configuration takes the following variables.

- number of robots
  - Number of robots to generate random positions for
- initial positions (can be random) : list of points in 2D
  - Initial robot positions that are randomly generated unless specified by the user
- speed of robots : number
- type of scheduler (default: async)
- probability distribution (default: exponential)
- visibility radius : number
  - Visibility radius of the robots
- orientation of robots: same or random (input as a list of triple(translation, rotation, reflection)) (NOT IMPLEMENTED)
- multiplicity detection
  - Detects if multiple robots are in the same point
- colors (NOT IMPLEMENTED)
- obstructed visibility (NOT IMPLEMENTED)
- rigidity
  - Rigid movement allows the robot to reach it's destination when in the MOVE state.
  - Non-rigid movement means the robot will fall short of it's destination when in the MOVE state.

## Default Configuration

- Unlimited visibility
- No Multiplicity detection
- Ignore Collisions
- Transparent robots
- Rigid movement

## To Do

### Fred and Georgin

- [ ] Add lights to the robot properties
- [ ] Make a function for changing colors
- [ ] Add rotation/reflection to look preprocessing
- [ ] Implement the canvas zoom in/out
- [ ] Implement sampling rate for faster animation
- [ ] Add a custom function file for algorithms for arbitrary change from browser event
- [ ] Add options for computing simulation properties, such as total distance traveled, total time taken, etc.

### Shereen

- [ ] Add faults to robot properties
- [ ] Add obstructed visibility 
- [ ] Add limited visibility
- [ ] Implement gathering with limited visibility algorithm
