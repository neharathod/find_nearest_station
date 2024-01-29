# authentication.py
import redis
import logging
from flask import request, jsonify

from redis_cache import RedisCache
from constants import *

class Authentication:
    def __init__(self):
        try:
            self.redis_client = RedisCache._instance
        except Exception as e:
            logging.error(f"Failed to initialize Redis connection: {str(e)}")
            raise SystemExit("Error initializing Redis connection.")

    # Function to check if the API_KEY provided is valid
    def is_valid_api_key(self, api_key):
        return api_key in VALID_API_KEYS

    # Function to check if the request rate is within limits
    def is_request_rate_limited(self, ip_address, api_key):
        # Check if the request count for the IP address or API key is below a threshold
        request_count_key = f"request_count:{ip_address}:{api_key}"
        current_request_count = int(self.redis_client.get(request_count_key) or 0)

        if current_request_count >= RATE_LIMIT_THRESHOLD:
            return False

        # Increment the request count and set an expiration
        self.redis_client.incr(request_count_key)
        self.redis_client.expire(request_count_key, RATE_LIMIT_THRESHOLD)

        return True

    # Decorator to require authentication and rate limiting for API routes
    def authenticate_and_rate_limit(self, f):
        def decorated_function(*args, **kwargs):
            # Authentication check
            api_key = request.args.get(API_KEY)
            if not api_key or not self.is_valid_api_key(api_key):
                logging.error("Unauthorized access: Invalid API key.")
                return jsonify({"error": "Unauthorized access to the API"}), 401

            # Rate limiting check
            ip_address = request.remote_addr
            if not self.is_request_rate_limited(ip_address, api_key):
                logging.warning(f"Rate limit exceeded for {ip_address}")
                return jsonify({"error": "Rate limit exceeded"}), 429

            return f(*args, **kwargs)

        return decorated_function
