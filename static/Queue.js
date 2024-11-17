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
