import json
import socket
from time import sleep
from robot import Robot
from scheduler import Scheduler
import numpy as np
import logging
from flask import Flask, jsonify, request, Response, send_from_directory
import webbrowser
import threading
import json
from flask_socketio import SocketIO, emit


logging.basicConfig(level=logging.INFO, filename="log.txt", filemode="w", format="")


def clear_log():
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(level=logging.INFO, filename="log.txt", filemode="w", format="")


# Disable Flask’s default logging to the root logger
log = logging.getLogger(
    "werkzeug"
)  # 'werkzeug' is the logger used by Flask for requests
log.setLevel(logging.ERROR)  # Set Flask's logging to a different level or disable it

app = Flask(__name__, static_folder="static")
socketio = SocketIO(app)

seed = np.random.default_rng().integers(0, 2**32 - 1)
generator = np.random.default_rng(seed=seed)

# num_of_robots = config["number_of_robots"]
# initial_positions = config["initial_positions"]

num_of_robots = 10
initial_positions = generator.uniform(low=-25, high=25, size=(num_of_robots, 2))


# WebSocket event handler for the simulation
@socketio.on("start_simulation")
def handle_simulation_request(data):
    scheduler = Scheduler(
        seed=seed,
        num_of_robots=num_of_robots,
        initial_positions=initial_positions,
        robot_speeds=data["robot_speeds"],
        rigid_movement=data["rigid_movement"],
        time_precision=data["time_precision"],
        threshold_precision=data["threshold_precision"],
        sampling_rate=data["sampling_rate"],
        labmda_rate=data["labmda_rate"],
    )

    def run_simulation():
        with app.app_context():
            while True:
                exit_code = scheduler.handle_event()
                if exit_code == 0:
                    snapshots = scheduler.visualization_snapshots
                    if len(snapshots) > 0:
                        socketio.emit(
                            "simulation_data",
                            json.dumps(scheduler.visualization_snapshots[-1]),
                        )

                if exit_code < 0:
                    # Signal the end of the simulation
                    socketio.emit("simulation_end", "END")
                    break

    # Start a thread for the simulation to not block websocket
    threading.Thread(target=run_simulation).start()


@socketio.on("connect")
def client_connect():
    print("Client connected")


@socketio.on("disconnect")
def client_disconnect():
    print("Client disconnected")


@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def open_browser(port):
    webbrowser.open(f"http://127.0.0.1:{port}/")


port = 8080
while is_port_in_use(port):
    port += 1

# Open the browser after a delay to let the server start
threading.Timer(1, open_browser, args=(port,)).start()
app.run(host="127.0.0.1", port=port, debug=True, use_reloader=False)
