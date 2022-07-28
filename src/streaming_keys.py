import json
import time
import jwt


class StreamingKeysService:
    def __init__(self, key: str, expiration_delta: int):
        self._key = key
        self.expiration_delta = expiration_delta

    def _encode(self, data: dict) -> str:
        return jwt.encode(data, self._key, algorithm="HS256")

    def _decode(self, data: str) -> str:
        return jwt.decode(data, self._key, algorithms=["HS256"])

    def get_streamer_key(self, streamer_username: str) -> str:
        """Returns key accepted by nginx-rtmp endpoint for publishing content"""
        return self._encode({"username": streamer_username})

    def get_watch_stream_key(self, streamer_username: str) -> str:
        """
        Returns key which is valid only for 10 minutes and can
        be used for watching streams of given streamer
        """
        return self._encode({"watch_stream": streamer_username, "iat": int(time.time())})
        

    def verify_streamer_key(self, key: str) -> bool:
        """Verifies that the streamer key is valid"""
        try:
            data = self._decode(key)
            return "username" in data
        except:
            return False

    def verify_watch_stream_key(self, key: str) -> tuple[bool, str]:
        """Verifies key for stream watching and returns streamer key"""
        try:
            data = self._decode(key)
            streamer_username = data["watch_stream"]
            iat = data["iat"]
            current_time = int(time.time())
            if iat + self.expiration_delta <= current_time:
                return False, None
            return True, streamer_username
        except:
            return False, None
