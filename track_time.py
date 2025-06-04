import time
import asyncio
import csv
from functools import wraps


def track_time(fn=None, *, id=None):
    if fn is None:
        return lambda fn: track_time(fn, id=id)

    @wraps(fn)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()

        result = await fn(*args, **kwargs)

        end_time = time.time()

        write_to_csv(id or fn.__name__, start_time, end_time)

        return result

    @wraps(fn)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()

        result = fn(*args, **kwargs)

        end_time = time.time()

        write_to_csv(id or fn.__name__, start_time, end_time)

        return result

    def write_to_csv(identifier, start_time, end_time):
        elapsed_time = end_time - start_time
        with open("out/timing_results.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    identifier,
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)),
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time)),
                    elapsed_time,
                ]
            )
        # Print the fields to the console
        print(f"ID: {identifier}")
        print(
            f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}"
        )
        print(
            f"End Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}"
        )
        print(f"Elapsed Time: {elapsed_time}")

    if asyncio.iscoroutinefunction(fn):
        return async_wrapper
    else:
        return sync_wrapper
