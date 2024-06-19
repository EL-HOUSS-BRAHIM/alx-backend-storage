#!/usr/bin/env python3
""" A module for using the Redis NoSQL data storage. """
import redis
import requests
from typing import Callable
from functools import wraps


def count_requests(method: Callable) -> Callable:
    """
    Decorator to count how many times a URL has been requested.
    """
    @wraps(method)
    def wrapper(self, url: str, *args, **kwargs) -> str:
        key = f"count:{url}"
        self._redis.incr(key)
        return method(self, url, *args, **kwargs)
    return wrapper


def cache_with_expiry(method: Callable) -> Callable:
    """
    Decorator to cache the result of the URL request with an expiry time.
    """
    @wraps(method)
    def wrapper(self, url: str, *args, **kwargs) -> str:
        cached_key = f"cached:{url}"
        cached_content = self._redis.get(cached_key)
        if cached_content:
            return cached_content.decode('utf-8')

        result = method(self, url, *args, **kwargs)
        self._redis.setex(cached_key, 10, result)
        return result
    return wrapper


class WebCache:
    """WebCache class to handle caching of web pages with Redis."""

    def __init__(self):
        """Initialize the WebCache instance with a Redis client."""
        self._redis = redis.Redis()

    @count_requests
    @cache_with_expiry
    def get_page(self, url: str) -> str:
        """
        Get the HTML content of a URL and cache it with an expiration time.

        Args:
            url (str): The URL to get the content from.

        Returns:
            str: The HTML content of the URL.
        """
        response = requests.get(url)
        return response.text
