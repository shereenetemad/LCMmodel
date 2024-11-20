import json
import socket
from scheduler import Scheduler
import numpy as np
import logging
from flask import Flask, jsonify, request, Response, send_from_directory
import webbrowser
import threading
import json
from flask_socketio import SocketIO, emit
from datetime import datetime
import os


def get_log_name():
    date = datetime.now()
    milliseconds = date.microsecond // 1000

    return f"{date.year}-{date.month}-{date.day}-{date.hour}-{date.minute}-{date.second}-{milliseconds}.txt"


def setup_parent_logger():
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)

    # Remove all existing file handlers
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)

    # Add a new file handler
    log_dir = "./logs/"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{get_log_name()}")

    new_file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter("")
    new_file_handler.setFormatter(formatter)
    logger.addHandler(new_file_handler)


# Disable Flask’s default logging to the root logger
log = logging.getLogger(
    "werkzeug"
)  # 'werkzeug' is the logger used by Flask for requests
log.setLevel(logging.ERROR)  # Set Flask's logging to a different level or disable it

app = Flask(__name__, static_folder="static")
socketio = SocketIO(app)

simulation_thread = None
terminate_flag = False


# WebSocket event handler for the simulation
@socketio.on("start_simulation")
def handle_simulation_request(data):
    global simulation_thread, terminate_flag

    setup_parent_logger()

    seed = data["random_seed"]
    generator = np.random.default_rng(seed=seed)
    num_of_robots = data["num_of_robots"]
    initial_positions: list = data["initial_positions"]

    if len(initial_positions) != 0:
        # User defined
        initial_positions = data["initial_positions"]
        num_of_robots = len(initial_positions)
    else:
        # Random
        initial_positions = generator.uniform(low=-25, high=25, size=(num_of_robots, 2))

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
        algorithm=data["algorithm"],
    )

    def run_simulation():
        global terminate_flag

        with app.app_context():
            while terminate_flag != True:
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

    # Terminate existing simulation thread
    if simulation_thread and simulation_thread.is_alive():
        logging.info("Terminating existing simulation thread.")
        terminate_flag = True
        simulation_thread.join()

    # Reset the termination flag and start a new simulation thread
    terminate_flag = False
    # Start a thread for the simulation to not block websocket
    simulation_thread = threading.Thread(target=run_simulation)
    simulation_thread.start()


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
