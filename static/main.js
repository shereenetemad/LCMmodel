window.addEventListener("resize", resizeCanvas);

// Elements
let canvas = /** @type {HTMLCanvasElement} */ (document.getElementById("canvas"));
let ctx = /** @type {CanvasRenderingContext2D} */ (canvas.getContext("2d"));

/** @type {Object.<number, Robot>}*/
let robots = {};
let snapshotQueue = new Queue();

let paused = false;
let timePerFrameMs = 17;
let lastFrameTime = 0;
let stopAnimation = false;

resizeCanvas();

//@ts-ignore
const socket = io(window.location.host);

socket.on("simulation_data", function (data) {
  startDrawingLoop();
  const _data = JSON.parse(data);
  snapshotQueue.enqueue(_data);
});

socket.on("simulation_end", function (message) {
  console.log("Simulation complete.");
});

const configOptions = {
  number_of_robots: 3,
  user_robots: false,
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
};

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

const startSimulation = {
  start_simulation: () => {
    snapshotQueue = new Queue();
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

/**
 * Draws a Robot on the canvas
 * @param {CanvasRenderingContext2D} ctx - Canvas context
 * @param {Robot} robot
 */
function drawRobot(ctx, robot) {
  ctx.beginPath();

  // Draw circle
  ctx.arc(robot.x, robot.y, robot.radius, 0, Math.PI * 2);
  ctx.fillStyle = robot.color;
  ctx.strokeStyle = robot.color;
  ctx.fill();
  ctx.stroke();
  ctx.closePath();

  // // Draw node label
  ctx.beginPath();
  ctx.strokeStyle = "#FFF";
  ctx.strokeText(robot.id, robot.x, robot.y);
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

  gui.add(configOptions, "number_of_robots");
  gui.add(configOptions, "user_robots");
  gui.add(configOptions, "rigid_movement");
  gui.add(configOptions, "multiplicity_detection");
  gui.add(configOptions, "obstructed_visibility");
  gui.add(configOptions, "robot_speeds", 0.1, 10, 0.1);
  gui.add(configOptions, "scheduler_type", schedulerTypes);
  gui.add(configOptions, "probability_distribution", probabilityDistributions);
  gui.add(configOptions, "visibility_radius");
  gui.add(configOptions, "time_precision");
  gui.add(configOptions, "threshold_precision");
  gui.add(configOptions, "sampling_rate");
  gui.add(configOptions, "labmda_rate");
  gui.add(configOptions, "algorithm", algorithmOptions).name("Algorithm");
  gui.add(startSimulation, "start_simulation");

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

  function updateConfig() {
    configOptions = { ...configOptions };
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

    robots[id].updatePosition(x, y);
    drawRobot(ctx, robots[id]);
  }
}

function updateTimeElement(time) {
  const timeElem = /** @type {HTMLElement}*/ (document.getElementById("time-value"));

  timeElem.innerText = time;
}
