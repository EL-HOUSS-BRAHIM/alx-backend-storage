#!/usr/bin/env python3
"""
A module for using the Redis NoSQL data storage.
"""

import uuid
import redis
from functools import wraps
from typing import Any, Callable, Union, Optional


def count_calls(method: Callable) -> Callable:
    """
    Decorator to count the number of times a method is called.
    The count is stored in Redis, using the method's qualified name as the key.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs for a method.
    The inputs and outputs are stored in Redis lists, using the method's
    qualified name with ":inputs" and ":outputs" suffixes as keys.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        self._redis.rpush(input_key, str(args))
        output = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(output))

        return output
    return wrapper


def replay(method: Callable) -> None:
    """
    Display the history of calls to a particular method.

    Args:
        method (Callable): The method to replay.
    """
    if method is None or not hasattr(method, '__self__'):
        return
    redis_store = getattr(method.__self__, '_redis', None)
    if not isinstance(redis_store, redis.Redis):
        return

    method_name = method.__qualname__
    input_key = f"{method_name}:inputs"
    output_key = f"{method_name}:outputs"

    inputs = redis_store.lrange(input_key, 0, -1)
    outputs = redis_store.lrange(output_key, 0, -1)

    print(f"{method_name} was called {len(inputs)} times:")
    for inp, outp in zip(inputs, outputs):
        print(f"{method_name}(*{inp.decode('utf-8')}) -> {outp.decode('utf-8')}")


class Cache:
    """Cache class to interact with Redis database."""

    def __init__(self) -> None:
        """
        Initialize the Cache instance.
        Create a Redis client and flush the database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with a randomly generated UUID key.

        Args:
            data (Union[str, bytes, int, float]): The data to store.

        Returns:
            str: The key under which the data is stored.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """
        Retrieve data from Redis by key and optionally apply a conversion function.

        Args:
            key (str): The key to retrieve.
            fn (Optional[Callable]): A function to convert the data.

        Returns:
            Union[str, bytes, int, float, None]: The retrieved data, optionally converted.
        """
        value = self._redis.get(key)
        return fn(value) if value is not None and fn is not None else value

    def get_str(self, key: str) -> str:
        """
        Retrieve a string from Redis by key.

        Args:
            key (str): The key to retrieve.

        Returns:
            str: The retrieved string.
        """
        return self.get(key, lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """
        Retrieve an integer from Redis by key.

        Args:
            key (str): The key to retrieve.

        Returns:
            int: The retrieved integer.
        """
        return self.get(key, int)
