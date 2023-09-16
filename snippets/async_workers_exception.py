import asyncio
import time
from datetime import datetime

from rich.console import Console

WORK_ITEM_COUNT = 10
FAIL_ITEMS_DIVISIBLE_BY = 7
PARALLELISM = 5
SLEEP_FOR = 1

console = Console()


async def worker(name: str, queue: asyncio.Queue, color: str):
    while True:
        # Get work item from queue
        work_item = await queue.get()

        # Do work
        if work_item % FAIL_ITEMS_DIVISIBLE_BY == 0:
            raise Exception(f"Failed processing item-{work_item}.")
        await asyncio.sleep(SLEEP_FOR)
        time = datetime.utcnow().time()
        console.print(f"{time} item-{work_item} processed by {name}.", style=color)

        # Notify the queue that the task is complete
        queue.task_done()


async def main():

    # Create async queue
    queue = asyncio.Queue()

    # Enqueue work items
    for i in range(1, WORK_ITEM_COUNT + 1):
        queue.put_nowait(i)

    # Create workers
    tasks = []
    for i in range(1, PARALLELISM + 1):
        task = asyncio.create_task(worker(f"worker-{i}", queue, color=f"color({i})"))
        tasks.append(task)

    # Convert queue.join() to a full-fledged task, so we can test whether it's done
    queue_complete = asyncio.create_task(queue.join())

    # wait for the queue to complete or one of the workers to exit
    await asyncio.wait([queue_complete, *tasks], return_when=asyncio.FIRST_COMPLETED)

    error = None

    if (
        not queue_complete.done()
    ):  # if queue processing is not complete, a worker task has raised
        console.print(
            "An item processing failed - shutting down all workers...", style="red"
        )
        for task in tasks:
            if task.done():  # task can be done only if it raised
                error = task.exception()
            else:
                task.cancel()
    else:
        console.print(
            "All tasks were processed succesfully - shutting down all workers...",
            style="green",
        )
        for task in tasks:
            task.cancel()

    # Block until all worker tasks are cancelled
    await asyncio.gather(*tasks, return_exceptions=True)

    # Propagate error
    if error:
        raise error


if __name__ == "__main__":
    start = time.monotonic()
    asyncio.run(main())
    elapsed = time.monotonic() - start
    print(f"Items processed in {round(elapsed, 2)} seconds.")
