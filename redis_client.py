import json
import sys
from datetime import timedelta
import redis
import httpx

def redis_connect() -> redis.client.Redis:
    try:
        client = redis.Redis(
            host="localhost",
            port=6379,
            password="",
            db=0,
            socket_timeout=5,
        )
        ping = client.ping()
        if ping is True:
            print("Connected to redis")
            return client
    except redis.AuthenticationError:
        print("AuthenticationError")
        sys.exit(1)

def get_routes_from_cache(key: str) -> str:
    """Data from redis."""

    val = client.get(key)
    return val


def set_routes_to_cache(key: str, value: str) -> bool:
    """Data to redis."""

    state = client.setex(key, timedelta(seconds=3600), value=value,)
    return state

def route_optima(query, keyvalue: str) -> dict:

    # First it looks for the data in redis cache
    data = get_routes_from_cache(key=keyvalue)

    # If cache is found then serves the data from cache
    if data is not None:
        data = json.loads(data)
        data["cache"] = True
        return data

    else:
        # If cache is not found then sends request to the MapBox API
        data = query.all()

        # This block sets saves the respose to redis and serves it directly
        if data.get("code") == "Ok":
            data["cache"] = False
            data = json.dumps(data)
            state = set_routes_to_cache(key=keyvalue, value=data)

            if state is True:
                return json.loads(data)
        return data
