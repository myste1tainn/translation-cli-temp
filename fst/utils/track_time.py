from typing import Callable, TypeVar, Any
import asyncio
import time
import csv
from functools import wraps

T = TypeVar("T", bound=Callable[..., Any])


def track_time(fn: T, *, id: str | None = None) -> T:
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
        print(f"ID: {identifier}")
        print(
            f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}"
        )
        print(
            f"End Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}"
        )
        print(f"Elapsed Time: {elapsed_time}")

    if asyncio.iscoroutinefunction(fn):
        return async_wrapper  # type: ignore
    else:
        return sync_wrapper  # type: ignore
