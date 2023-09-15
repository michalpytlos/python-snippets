import asyncio
import time
from datetime import datetime

from rich.console import Console

WORK_ITEM_COUNT = 10
PARALLELISM = 5
SLEEP_FOR = 1

console = Console()


async def worker(name: str, queue: asyncio.Queue, color: str):
    while True:
        # Get work item from queue
        work_item = await queue.get()  # return control if queue is empty

        # Do work
        await asyncio.sleep(SLEEP_FOR)  # return control while waiting
        time = datetime.utcnow().time()
        console.print(f"{time} {work_item} processed by {name}.", style=color)

        # Notify the queue that the task is complete
        queue.task_done()


async def main():

    # Create async queue
    queue = asyncio.Queue()

    # Enqueue work items
    for i in range(WORK_ITEM_COUNT):
        queue.put_nowait(f"item-{i}")

    # Create workers
    tasks = []
    for i in range(PARALLELISM):
        # Wrap the worker coroutine into a Task and schedule its execution. Return the Task object.
        task = asyncio.create_task(worker(f"worker-{i}", queue, color=f"color({i})"))
        tasks.append(task)

        # Tasks are used to run coroutines in event loops. If a coroutine awaits on a Future,
        # the Task suspends the execution of the coroutine and waits for the completion of the Future.
        # When the Future is done, the execution of the wrapped coroutine resumes.
        # Event loops use cooperative scheduling: an event loop runs one Task at a time.
        # While a Task awaits for the completion of a Future, the event loop runs other Tasks,
        # callbacks, or performs IO operations.
        # https://docs.python.org/3/library/asyncio-task.html#asyncio.Task

    # Block until all items in the queue have been gotten and processed
    await queue.join()

    # Cancel worker tasks
    for task in tasks:
        task.cancel()

    # Block until all worker tasks are cancelled
    await asyncio.gather(
        *tasks, return_exceptions=True
    )  # return a future aggregating results from the given coroutines


if __name__ == "__main__":
    start = time.monotonic()
    # Run the main coroutine, taking care of managing the asyncio event loop, finalizing async generators and closing the threadpool.
    asyncio.run(main())
    elapsed = time.monotonic() - start
    print(f"Items processed in {round(elapsed, 2)} seconds.")
