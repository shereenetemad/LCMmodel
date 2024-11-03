// @ts-nocheck

window.addEventListener("resize", resizeCanvas);

// Constants
const ROBOT_SIZE = 6;

let canvas = document.getElementById("canvas");
let ctx = canvas.getContext("2d");

let window_height = window.innerHeight;
let window_width = window.innerWidth;

resizeCanvas();
let robots = {};

class Robot {
  constructor(x, y, id, color, speed) {
    this.x = x;
    this.y = y;
    this.id = id;
    this.color = color;
    this.speed = speed;
    this.radius = ROBOT_SIZE;
    this.dx = 1 * this.speed;
    this.dy = 1 * this.speed;
  }

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

document.addEventListener("DOMContentLoaded", function () {
  fetch("http://127.0.0.1:8080/api/data") // Ensure URL matches backend's route and port
    .then((response) => response.json())
    .then((data) => {
      console.log("Snapshots");
      console.log(data.snapshots);
      let i = 0;
      let intervalID = setInterval(() => {
        if (i < data.snapshots.length) {
          clearCanvas();
          drawSnapshot(data.snapshots[i]);
          i++;
        } else {
          clearInterval(intervalID);
        }
      }, 500);
    })
    .catch((error) => console.error("Error fetching data:", error));
});

function drawSnapshot(snapshot) {
  let time = snapshot[0];
  updateTimeElement(time);
  let robotsHistory = snapshot[1];
  for (let id in robotsHistory) {
    console.log(id);
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
