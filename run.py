import json
from robot import *



with open('config.json', 'r') as file:
    config = json.load(file)

print(config)