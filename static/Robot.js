class Robot {
  static ROBOT_SIZE = 8;
  static ROBOT_POS_FACTOR = 10;

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
    /** @type {number} */ this.x = x * Robot.ROBOT_POS_FACTOR;
    /** @type {number} */ this.y = y * Robot.ROBOT_POS_FACTOR;
    /** @type {string} */ this.id = id;
    /** @type {string} */ this.color = color;
    /** @type {number} */ this.speed = speed;
    /** @type {number} */ this.radius = Robot.ROBOT_SIZE;
  }

  /**
   * @param {number} x - New X position
   * @param {number} y - New Y position
   */
  updatePosition(x, y) {
    this.x = x * Robot.ROBOT_POS_FACTOR;
    this.y = y * Robot.ROBOT_POS_FACTOR;
  }
}
