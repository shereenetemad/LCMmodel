import json
from time import sleep
from robot import Robot
from scheduler import Scheduler


with open("config.json", "r") as file:
    config = json.load(file)

print(config)

if isinstance(config["initial_positions"], list) and config["number_of_robots"] != len(
    config["initial_positions"]
):
    raise Exception(
        "Error in config.json: length of the initial_positions array must be the same as the value in num_of_robots"
    )

if isinstance(config["robot_speeds"], list) and config["number_of_robots"] != len(
    config["robot_speeds"]
):
    raise Exception(
        "Error in config.json: length of the robot_speeds array must be the same as the value in num_of_robots"
    )

if isinstance(config["robot_orientations"], list) and config["number_of_robots"] != len(
    config["robot_orientations"]
):
    raise Exception(
        "Error in config.json: length of the robot_orientations array must be the same as the value in num_of_robots"
    )

if isinstance(config["robot_colors"], list) and config["number_of_robots"] != len(
    config["robot_colors"]
):
    raise Exception(
        "Error in config.json: length of the robot_colors array must be the same as the value in num_of_robots"
    )

scheduler = Scheduler(
    num_of_robots=config["number_of_robots"],
    initial_positions=config["initial_positions"],
    robot_speeds=config["robot_speeds"],
)

for i in range(10):
    scheduler.handle_event()
