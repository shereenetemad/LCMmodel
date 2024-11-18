window.addEventListener("resize", resizeCanvas);

// Elements
let canvas = /** @type {HTMLCanvasElement} */ (document.getElementById("canvas"));
let ctx = /** @type {CanvasRenderingContext2D} */ (canvas.getContext("2d"));
let time = /**@type {HTMLElement} */ (document.getElementById("time-value"));
let message = /**@type {HTMLElement} */ (document.getElementById("message"));

/** @type {Object.<number, Robot>}*/
let robots = {};
let snapshotQueue = new Queue();

let paused = false;
let timePerFrameMs = 17;
let lastFrameTime = 0;
let stopAnimation = false;
let currRobotId = 0;

resizeCanvas();

//@ts-ignore
const socket = io(window.location.host);

socket.on("simulation_data", function (data) {
  startDrawingLoop();
  const _data = JSON.parse(data);
  snapshotQueue.enqueue(_data);
});

socket.on("simulation_end", function (message) {
  // simulationRunning = false;
  console.log("Simulation complete.");
});

const schedulerTypes = {
  Async: "Async",
  Sync: "Sync",
};

const probabilityDistributions = {
  Exponential: "Exponential",
  Gaussian: "Gaussian",
};

const algorithmOptions = {
  Gathering: "Gathering",
  SEC: "Smallest Enclosing Circle",
};

const initialPositionsOptions = {
  Random: "Random",
  "User Defined": "User Defined",
};

const startSimulation = {
  start_simulation: () => {
    snapshotQueue = new Queue();
    clearCanvas();
    paused = false;
    gui.updatePauseText();
    socket.emit("start_simulation", configOptions);
  },
};

const togglePause = {
  pause_simulation: () => {
    paused = true;
  },
  play_simulation: () => {
    paused = false;
  },
};

const configOptions = {
  num_of_robots: 3,
  initialization_method: "Random",
  /** @type {Array}*/ initial_positions: [],
  robot_speeds: 1.0,
  scheduler_type: "Async",
  probability_distribution: "Exponential",
  visibility_radius: 100,
  robot_orientations: null,
  multiplicity_detection: false,
  robot_colors: "#000000",
  obstructed_visibility: false,
  rigid_movement: true,
  time_precision: 4,
  threshold_precision: 5,
  sampling_rate: 0.2,
  labmda_rate: 10,
  algorithm: "Gathering",
  random_seed: Math.floor(Math.random() * (2 ** 32 - 1)) + 1,
};

/**
 * Draws a Robot on the canvas
 * @param {CanvasRenderingContext2D} ctx - Canvas context
 * @param {Robot} robot
 */
function drawRobot(ctx, robot) {
  ctx.beginPath();

  // Draw circle
  const [x, y] = robot.getCanvasPosition();
  ctx.arc(x, y, robot.radius, 0, Math.PI * 2);
  ctx.fillStyle = robot.color;
  ctx.strokeStyle = robot.color;
  ctx.fill();
  ctx.stroke();
  ctx.closePath();

  // // Draw node label
  ctx.beginPath();
  ctx.strokeStyle = "#FFF";
  ctx.strokeText(robot.id, x, y);
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.font = "9px Arial";
  ctx.fill();
  ctx.stroke();
  ctx.closePath();
}

const gui = setupOptions(configOptions);

function setupOptions(configOptions) {
  //@ts-ignore
  const gui = new dat.GUI();

  const numRobotsController = gui.add(configOptions, "num_of_robots", 1, 50, 1);
  gui
    .add(configOptions, "initialization_method", initialPositionsOptions)
    .name("Positions")
    .onFinishChange(changeInitializationMethod);
  gui.add(configOptions, "rigid_movement");
  gui.add(configOptions, "multiplicity_detection");
  gui.add(configOptions, "obstructed_visibility");
  gui.add(configOptions, "robot_speeds", 0.1, 10, 0.1);
  gui.add(configOptions, "scheduler_type", schedulerTypes);
  gui.add(configOptions, "probability_distribution", probabilityDistributions);
  gui.add(configOptions, "visibility_radius", 1, 100, 1);
  gui.add(configOptions, "time_precision", 1, 10, 1);
  gui.add(configOptions, "threshold_precision", 1, 10, 1);
  gui.add(configOptions, "sampling_rate", 0.01, 0.5, 0.01);
  gui.add(configOptions, "labmda_rate");
  gui.add(configOptions, "algorithm", algorithmOptions).name("Algorithm");
  gui.add(configOptions, "random_seed", 1, 2 ** 32 - 1, 1).name("Seed");
  gui.add(startSimulation, "start_simulation").name("Start simulation");

  const pauseController = gui
    .add(togglePause, "pause_simulation")
    .name("Pause")
    .onFinishChange(updatePauseText);

  function updatePauseText() {
    if (paused) {
      pauseController.name("Play");
      pauseController.property = "play_simulation";
    } else {
      pauseController.name("Pause");
      pauseController.property = "pause_simulation";
    }
  }

  function changeInitializationMethod() {
    const numRobotsControllerElement = numRobotsController.domElement;
    if (configOptions.initialization_method === initialPositionsOptions.Random) {
      numRobotsControllerElement.parentElement.parentElement.style.display = "list-item";
      numRobotsController.setValue(3);

      canvas.removeEventListener("click", handleCanvasClick);

      clearSimulation();
    } else {
      numRobotsControllerElement.parentElement.parentElement.style.display = "none";
      numRobotsController.setValue(0);
      message.style.display = "block";

      canvas.addEventListener("click", handleCanvasClick);

      clearSimulation();
    }
  }

  return { gui, updatePauseText };
}

function startDrawingLoop() {
  // requestAnimationFrame initiates the animation loop
  stopAnimation = false;
  requestAnimationFrame(drawLoop); // Start the loop
}

function stopDrawingLoop() {
  stopAnimation = true;
}

function drawLoop(currentTime) {
  if (stopAnimation) {
    return;
  }
  // Calculate the time since the last frame
  const deltaTime = currentTime - lastFrameTime;

  // Check if enough time has passed to render a new frame
  if (deltaTime >= timePerFrameMs && !paused) {
    const snapshot = snapshotQueue.dequeue();
    if (snapshot) {
      clearCanvas();
      drawSnapshot(snapshot);
      lastFrameTime = currentTime; // Reset lastFrameTime for the next frame
    } else {
      stopDrawingLoop();
      return;
    }
  }

  // Request the next frame
  requestAnimationFrame(drawLoop);
}

function clearCanvas() {
  ctx.clearRect(-canvas.width / 2, -canvas.height / 2, canvas.width, canvas.height);
}

function getRandomColor() {
  const r = Math.floor(50 + Math.random() * 256);
  const g = Math.floor(50 + Math.random() * 256);
  const b = Math.floor(50 + Math.random() * 256);

  return `rgb(${r}, ${g}, ${b})`;
}

function resizeCanvas() {
  // This function resets the canvas
  console.log("Resized Canvas");

  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  // Translate the coordinate system to be in the center
  ctx.translate(canvas.width / 2, canvas.height / 2);
}

function drawSnapshot(snapshot) {
  let time = snapshot[0];
  updateTimeElement(time);
  let robotsHistory = snapshot[1];
  for (let id in robotsHistory) {
    let [x, y] = robotsHistory[id][0];
    if (robots[id] === undefined) {
      robots[id] = new Robot(x, y, id, "black", 1);
    }

    robots[id].setPosition(x, y);
    drawRobot(ctx, robots[id]);
  }
}

function updateTimeElement(t) {
  time.innerText = t;
}

/**
 * @param {MouseEvent} e
 */
function handleCanvasClick(e) {
  if (time.innerText !== "") {
    clearSimulation();
  }

  console.log(e);
  const x = e.offsetX;
  const y = e.offsetY;

  const [canvasX, canvasY] = translateToCanvas(canvas, x, y);

  const robot = new Robot(
    canvasX,
    canvasY,
    `${currRobotId++}`,
    configOptions.robot_colors,
    configOptions.robot_speeds,
    true
  );

  drawRobot(ctx, robot);

  configOptions.initial_positions.push(robot.getPosition());
  message.style.display = "none";
}

function clearSimulation() {
  clearCanvas();
  updateTimeElement("");

  robots = {};
  snapshotQueue = new Queue();
  lastFrameTime = 0;
  currRobotId = 0;
  configOptions.initial_positions = [];
}

/**
 * Converts mouse coordinates to coordinates on a canvas with origin at the center of screen
 * @param {HTMLCanvasElement} canvas - Canvas element
 * @param {number} x
 * @param {number} y
 */
function translateToCanvas(canvas, x, y) {
  return [x - canvas.width / 2, y - canvas.height / 2];
}
