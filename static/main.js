class Queue {
  /**
   * @typedef {{value: any, next: QueueNode | undefined}} QueueNode
   */

  constructor() {
    /** @type {QueueNode | undefined} */
    this.head = undefined;

    /** @type {QueueNode | undefined} */
    this.tail = undefined;
    this.size = 0;
  }

  enqueue(value) {
    /** @type {QueueNode} */
    const newNode = {
      value,
      next: undefined,
    };

    if (this.tail) {
      this.tail.next = newNode;
    } else {
      this.head = newNode;
    }
    this.tail = newNode;

    this.size++;
  }

  dequeue() {
    if (!this.head) {
      return undefined;
    }

    /** @type {QueueNode} */
    const value = this.head.value;
    this.head = this.head.next;

    if (!this.head) {
      this.tail = undefined;
    }

    this.size--;
    return value;
  }

  peek() {
    return this.head ? this.head.value : undefined;
  }
}

class Robot {
  /**
   * Represents a robot
   * @constructor
   * @param {number} x - X position
   * @param {number} y - Y position
   * @param {string} id - Robot's id
   * @param {string} color - Robot's color
   * @param {number} speed - Robot's speed
   */
  constructor(x, y, id, color, speed) {
    /** @type {number} */ this.x = x;
    /** @type {number} */ this.y = y;
    /** @type {string} */ this.id = id;
    /** @type {string} */ this.color = color;
    /** @type {number} */ this.speed = speed;
    /** @type {number} */ this.radius = ROBOT_SIZE;
  }

  /**
   * Draws a Robot on the canvas
   * @param {CanvasRenderingContext2D} ctx - Canvas context
   */
  draw(ctx) {
    ctx.beginPath();

    // Draw circle
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.fillStyle = this.color;
    ctx.strokeStyle = this.color;
    ctx.fill();
    ctx.stroke();
    ctx.closePath();

    // // Draw node label
    ctx.beginPath();
    ctx.strokeStyle = "#FFF";
    ctx.strokeText(this.id, this.x, this.y);
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.font = "9px Arial";
    ctx.fill();
    ctx.stroke();
  }

  /**
   * @param {number} x - New X position
   * @param {number} y - New Y position
   */
  updatePosition(x, y) {
    this.x = x * 10;
    this.y = y * 10;
  }

  update() {
    clearCanvas();
    this.draw(ctx);
  }
}

window.addEventListener("resize", resizeCanvas);

// Constants
const ROBOT_SIZE = 8;
// const eventSource = new EventSource("/api/data");

// Elements
let canvas = /** @type {HTMLCanvasElement} */ (document.getElementById("canvas"));
let pausePlayBtn = /** @type {HTMLButtonElement} */ (
  document.getElementById("pause-play-btn")
);

let ctx = /** @type {CanvasRenderingContext2D} */ (canvas.getContext("2d"));

// Global variables
/** @type {number} */
let window_height = window.innerHeight;

/** @type {number} */
let window_width = window.innerWidth;

/** @type {Object.<number, Robot>}*/
let robots = {};
let snapshotQueue = new Queue();

let paused = false;
let timePerFrameMs = 17;
let lastFrameTime = 0;
let stopAnimation = false;

pausePlayBtn.addEventListener("click", togglePausePlay);
resizeCanvas();

//@ts-ignore
const socket = io(window.location.host);

socket.emit("start_simulation", {});

socket.on("simulation_data", function (data) {
  startDrawingLoop();
  const _data = JSON.parse(data);
  snapshotQueue.enqueue(_data);
});

socket.on("simulation_end", function (message) {
  console.log("Simulation complete.");
});

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

let robot = new Robot(0, 0, "1", "red", 1);
robot.draw(ctx);

function getRandomColor() {
  const r = Math.floor(50 + Math.random() * 256);
  const g = Math.floor(50 + Math.random() * 256);
  const b = Math.floor(50 + Math.random() * 256);

  return `rgb(${r}, ${g}, ${b})`;
}

function resizeCanvas() {
  // This function resets the canvas
  console.log("Resized Canvas");
  window_height = window.innerHeight;
  window_width = window.innerWidth;
  canvas.width = window_width;
  canvas.height = window_height;

  // Translate the coordinate system to be in the center
  ctx.translate(canvas.width / 2, canvas.height / 2);
}

function drawSnapshot(snapshot) {
  let time = snapshot[0];
  updateTimeElement(time);
  let robotsHistory = snapshot[1];
  for (let id in robotsHistory) {
    if (robots[id] === undefined) {
      robots[id] = new Robot(0, 0, id, "black", 1);
    }

    let [x, y] = robotsHistory[id][0];
    robots[id].updatePosition(x, y);
    robots[id].draw(ctx);
  }
}

function updateTimeElement(time) {
  const timeElem = /** @type {HTMLElement}*/ (document.getElementById("time-value"));

  timeElem.innerText = time;
}

function togglePausePlay() {
  paused = !paused;

  if (paused) {
    pausePlayBtn.innerText = "Play";
  } else {
    pausePlayBtn.innerText = "Pause";
  }
}
