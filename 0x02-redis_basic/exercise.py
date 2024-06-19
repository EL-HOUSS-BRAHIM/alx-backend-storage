import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps
""" redis_basic module exercise"""


class Cache:
    """ Cache class
    """

    def __init__(self):
        """ Constructor method
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """ Method that generates a random key and stores the input data in Redis
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
