# redis_cache.py
import json
import redis
import logging

from constants import *

class RedisCache:
    _instance = None  # Class variable to store the instance

    # Create a single instance of the redis cache
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RedisCache, cls).__new__(cls)
            try:
                # Initialize Redis connection
                cls._instance.redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
            except Exception as e:
                logging.error(f"Failed to initialize Redis connection: {str(e)}")
                # raise SystemExit("Error initializing Redis connection.")
        return cls._instance

    def get(self, key):
        """
        Method to get value from the Redis store.
        Parameters:
            key: Location key to search for in Redis
        Returns:
            json result containing nearest station geojson
        """
        try:
            cached_result = self._instance.redis_client.get(key)
            return json.loads(cached_result.decode('utf-8')) if cached_result else None
        except Exception as e:
            logging.error(f"Error accessing cache for key '{key}': {str(e)}")
            return None

    def set(self, key, value, expiration_time=60):
        """
        Method to set key:value pair in Redis store
        Parameters:
            key: Location (latitude:longitude)
            value: Nearest station GeoJson object
            expiration_time: Time until which cache entry is valid (default: 60 seconds)
        Returns: None
        """
        try:
            self._instance.redis_client.setex(key, expiration_time, json.dumps(value))
        except Exception as e:
            logging.error(f"Error storing result in cache for key '{key}': {str(e)}")

    def incr(self, key):
        """
        Increment the value of a key in the cache.
        Parameters:
            key: The key to increment
        Returns:
            The incremented value
        """
        return self._instance.redis_client.incr(key)

    def expire(self, key, expiration_time):
        """
        Expire the value of a key in the cache.
        Parameters:
            key: The key to increment
            expiration_time: Time to expire
        """
        self._instance.redis_client.expire(key, expiration_time)
