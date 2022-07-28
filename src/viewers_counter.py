import redis
import time


class ViewersCounter:
    def __init__(self, redis: redis.Redis):
        self._redis = redis

    def add_viewer(self, streamer_username: str, viewer_ip: str):
        current_time = int(time.time())
        self._redis.set(
            f"viewers:{streamer_username}:{viewer_ip}", 1, ex=current_time + 600
        )

    def get_viewers_count(self, streamer_username: str):
        return len(self._redis.keys(f"viewers:{streamer_username}*"))
