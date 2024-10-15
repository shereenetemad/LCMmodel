import json
from robot import Robot
from scheduler import Scheduler


with open('config.json', 'r') as file:
    config = json.load(file)

print(config)

scheduler = Scheduler(num_of_robots=config["number_of_robots"], 
                      initial_positions= config["initial_positions"],
                      robot_speeds=config["robot_speeds"])