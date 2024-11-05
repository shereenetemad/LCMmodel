// @ts-nocheck

class Queue {
  constructor() {
    this.head = undefined;
    this.tail = undefined;
  }

  enqueue(value) {
    const newNode = { value, next: undefined };

    if (this.tail) {
      this.tail.next = newNode;
    } else {
      this.head = newNode;
    }
    this.tail = newNode;
  }

  dequeue() {
    if (!this.head) {
      return undefined;
    }

    const value = this.head.value;
    this.head = this.head.next;

    if (!this.head) {
      this.tail = undefined;
    }

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
   * @param {number} id - Robot's id
   * @param {string} color - Robot's color
   * @param {number} speed - Robot's speed
   */
  constructor(x, y, id, color, speed) {
    /** @type {number} */ this.x = x;
    /** @type {number} */ this.y = y;
    /** @type {number} */ this.id = id;
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
    // ctx.beginPath();
    // ctx.strokeStyle = "#000";
    // ctx.strokeText(this.id, this.x, this.y);
    // ctx.textAlign = "left";
    // ctx.font = "20px Arial";
    // ctx.stroke();
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

    this.x += this.dx;
    this.y += this.dy;
  }
}

window.addEventListener("resize", resizeCanvas);

// Constants
const ROBOT_SIZE = 6;

/** @type {HTMLCanvasElement} */
let canvas = document.getElementById("canvas");

/** @type {CanvasRenderingContext2D} */
let ctx = canvas.getContext("2d");

/** @type {number} */
let window_height = window.innerHeight;

/** @type {number} */
let window_width = window.innerWidth;

resizeCanvas();

/** @type {Object.<number, Robot>}*/
let robots = {};
let snapshotQueue = new Queue();

let intervalId = undefined;

const eventSource = new EventSource("/api/data");

eventSource.onmessage = function (event) {
  if (event.data === "END") {
    console.log("Simulation complete. Closing connection.");

    eventSource.close();
  } else {
    if (!intervalId) {
      startDrawingInterval();
    }
    const data = JSON.parse(event.data);
    snapshotQueue.enqueue(data);
  }
};

eventSource.onerror = function (event) {
  console.log("Error occured");
  eventSource.close();
};

function startDrawingInterval() {
  intervalId = setInterval(() => {
    const snapshot = snapshotQueue.dequeue();
    if (!snapshot) {
      clearInterval(intervalId);
      return;
    }
    clearCanvas();
    drawSnapshot(snapshot);
  }, 17);
}

function clearCanvas() {
  ctx.clearRect(-canvas.width / 2, -canvas.height / 2, canvas.width, canvas.height);
}

let robot = new Robot(0, 0, 1, "red", 1);
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
      robots[id] = new Robot(undefined, undefined, id, getRandomColor(), 1);
    }

    let [x, y] = robotsHistory[id][0];
    robots[id].updatePosition(x, y);
    robots[id].draw(ctx);
  }
}

function updateTimeElement(time) {
  document.getElementById("time-value").innerText = time;
}
