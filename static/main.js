// @ts-nocheck

window.addEventListener("resize", resizeCanvas);

// Constants
const ROBOT_SIZE = 4;

let canvas = document.getElementById("canvas");
let ctx = canvas.getContext("2d");

let window_height = window.innerHeight;
let window_width = window.innerWidth;

resizeCanvas();

class Robot {
  constructor(x, y, id, color, speed) {
    this.id = id;
    this.color = color;
    this.speed;
    this.x = x;
    this.y = y;
    this.radius = ROBOT_SIZE;
  }

  draw(ctx) {
    ctx.beginPath();
    ctx.strokeStyle = this.color;
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.fillStyle = this.color;
    ctx.fill();
    ctx.stroke();
  }

  update() {}
}

let robot = new Robot(0, 0, 1, "red", 1);
robot.draw(ctx);

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
      console.log(data.snapshots);
    })
    .catch((error) => console.error("Error fetching data:", error));
});
