import json
from time import sleep
from robot import Robot
from scheduler import Scheduler
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import logging


logging.basicConfig(level=logging.INFO, filename="log.txt", filemode="w", format="")


with open("config.json", "r") as file:
    config = json.load(file)


def clear_log():
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(level=logging.INFO, filename="log.txt", filemode="w", format="")


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


# num_of_robots = config["number_of_robots"]
# initial_positions = config["initial_positions"]

seed = np.random.default_rng().integers(0, 2**32 - 1)
generator = np.random.default_rng(seed=seed)

num_of_robots = 10
initial_positions = generator.uniform(low=-25, high=25, size=(num_of_robots, 2))

scheduler = Scheduler(
    seed=seed,
    num_of_robots=num_of_robots,
    initial_positions=initial_positions,
    robot_speeds=config["robot_speeds"],
    rigid_movement=config["rigid_movement"],
    time_precision=config["time_precision"],
    threshold_precision=config["threshold_precision"],
)


from flask import Flask, jsonify, request, Response, send_from_directory
import webbrowser
import threading
import json


# Disable Flask’s default logging to the root logger
log = logging.getLogger(
    "werkzeug"
)  # 'werkzeug' is the logger used by Flask for requests
log.setLevel(logging.ERROR)  # Set Flask's logging to a different level or disable it

app = Flask(__name__, static_folder="static")


@app.route("/api/data", methods=["GET"])
def get_data():
    clear_log()
    scheduler = Scheduler(
        seed=seed,
        num_of_robots=num_of_robots,
        initial_positions=initial_positions,
        robot_speeds=config["robot_speeds"],
        rigid_movement=config["rigid_movement"],
        time_precision=config["time_precision"],
        threshold_precision=config["threshold_precision"],
    )

    def run_simulation():
        while True:
            exit_code = scheduler.handle_event()

            if exit_code == 1:
                yield f"data:{json.dumps(scheduler.snapshot_history[-1])}\n\n"

            if exit_code < 0:
                yield "data:END\n\n"
                break

    return Response(run_simulation(), mimetype="text/event-stream")


@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")


def open_browser():
    webbrowser.open("http://127.0.0.1:8080/")


if __name__ == "__main__":
    threading.Timer(1, open_browser).start()  # Delay to give server time to start
    app.run(host="127.0.0.1", port=8080, debug=True, use_reloader=False)
