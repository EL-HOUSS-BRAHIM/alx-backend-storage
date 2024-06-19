import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps
""" Redis basic exercise module """


def count_calls(method: Callable) -> Callable:
    """Decorator to count the number of calls to a method"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper function to increment the call count
        and call the original method"""
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator to store the history of inputs and outputs for a function"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper function to store the input and output history"""
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        self._redis.rpush(input_key, str(args))

        output = method(self, *args, **kwargs)

        self._redis.rpush(output_key, str(output))

        return output
    return wrapper


def replay(method: Callable):
    """Display the history of calls of a particular function"""
    redis_client = method.__self__._redis
    method_name = method.__qualname__
    input_key = f"{method_name}:inputs"
    output_key = f"{method_name}:outputs"

    inputs = redis_client.lrange(input_key, 0, -1)
    outputs = redis_client.lrange(output_key, 0, -1)

    print(f"{method_name} was called {len(inputs)} times:")
    for inp, out in zip(inputs, outputs):
        print(f"{method_name}(*{inp.decode('utf-8')}) -> {
            out.decode('utf-8')}")


class Cache:
    def __init__(self):
        """Initialize the Cache class"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store the data in Redis with a random key and return the key"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(
        self,
        key: str,
        fn: Optional[Callable] = None
    ) -> Union[str, bytes, int, float, None]:
        """Retrieve the data from Redis using the key
        and optional conversion function"""
        data = self._redis.get(key)
        if data is None:
            return None
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> Optional[str]:
        """Retrieve the data from Redis as a string"""
        data = self.get(key, lambda d: d.decode("utf-8"))
        return data

    def get_int(self, key: str) -> Optional[int]:
        """Retrieve the data from Redis as an integer"""
        data = self.get(key, int)
        return data
