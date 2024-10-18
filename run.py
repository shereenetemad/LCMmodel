import json
from time import sleep
from robot import Robot
from scheduler import Scheduler
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


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


# COMMENT THESE OUT
num_of_robots = config["number_of_robots"]
initial_positions = config["initial_positions"]

# num_of_robots = 5
# initial_positions = np.random.uniform(low=-25, high=25, size=(5, 2))

scheduler = Scheduler(
    num_of_robots=num_of_robots,
    initial_positions=initial_positions,
    robot_speeds=config["robot_speeds"],
    rigid_movement=config["rigid_movement"],
)

for i in range(30):
    scheduler.handle_event()


robot_data = scheduler.snapshot_history
robot_ids = list(robot_data[0][1].keys())

fig, ax = plt.subplots()
ax.set_xlim(-30, 30)
ax.set_ylim(-30, 30)

# Plot for each robot (dots)
robot_plots = {}
for robot_id in robot_ids:
    (robot_plots[robot_id],) = ax.plot([], [], "o", label=f"Robot {robot_id}")

# Time text display
time_text = ax.text(0.02, 0.95, "", transform=ax.transAxes)


def init():
    """Initialize the plots."""
    for plot in robot_plots.values():
        plot.set_data([], [])
    time_text.set_text("")
    return list(robot_plots.values()) + [time_text]


def update(frame):
    """Update the robot positions and time for each frame."""
    time, positions = frame
    for robot_id, (pos, state) in positions.items():
        x, y = pos
        robot_plots[robot_id].set_data([x], [y])

    time_text.set_text(f"Time: {time:.4f}")
    return list(robot_plots.values()) + [time_text]


# Create animation
ani = FuncAnimation(
    fig,
    update,
    frames=robot_data,
    init_func=init,
    blit=True,
    interval=500,
    repeat=False,
)

plt.legend()
plt.show()
