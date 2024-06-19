import redis
import requests
from typing import Callable
from functools import wraps
# Initialize Redis client
redis_client = redis.Redis()
""" web module """


def count_requests(method: Callable) -> Callable:
    """Decorator to count the number of requests to a URL"""
    @wraps(method)
    def wrapper(url: str, *args, **kwargs):
        """Wrapper function to count the request and call the original method"""
        count_key = f"count:{url}"
        redis_client.incr(count_key)
        return method(url, *args, **kwargs)
    return wrapper


def cache_result(method: Callable) -> Callable:
    """Decorator to cache the result of a function for 10 seconds"""
    @wraps(method)
    def wrapper(url: str, *args, **kwargs):
        """Wrapper function to cache the result and call the original method"""
        cache_key = f"cache:{url}"
        cached_result = redis_client.get(cache_key)
        if cached_result:
            return cached_result.decode('utf-8')

        result = method(url, *args, **kwargs)
        redis_client.setex(cache_key, 10, result)
        return result
    return wrapper


@count_requests
@cache_result
def get_page(url: str) -> str:
    """Fetch the HTML content of a URL and return it"""
    response = requests.get(url)
    return response.text


# Test the function with a slow URL
if __name__ == "__main__":
    test_url = "http://slowwly.robertomurray.co.uk/delay/5000/url/https://www.example.com"

    # First call should fetch from the web and cache the result
    print("First call:")
    print(get_page(test_url))

    # Second call should return the cached result
    print("Second call:")
    print(get_page(test_url))

    # Wait for more than 10 seconds and fetch again to see the cache expiration
    import time
    time.sleep(11)

    print("Third call after cache expiration:")
    print(get_page(test_url))

    # Check the request count
    print(f"Request count for {test_url}: {
          redis_client.get(f'count:{test_url}').decode('utf-8')}")
