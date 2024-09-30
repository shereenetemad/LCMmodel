# Asynchronous Scheduler

A simulator for Look Compute Move robots in the Asynchronous System

## Running the Simulator

`python run.py config.json`

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
+ Scheduler Functions:
    -
    -
    -

+ Robot Functions:
    -
    -
    -

## Data Structures
+ Snapshot: Dictionary of ID, Position, Color (optional)
+ Priority Queue
