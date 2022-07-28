from pathlib import Path

import redis
from fastapi import FastAPI, Request, Depends
from fastapi.responses import FileResponse, JSONResponse

from streaming_keys import StreamingKeysService
from viewers_counter import ViewersCounter
import config


app = FastAPI()


def get_streaming_keys():
    yield StreamingKeysService(config.JWT_KEY, config.TOKEN_EXPIRATION_DELTA)


def get_redis() -> redis.Redis:
    yield redis.Redis(config.REDIS_URL)


def get_viewers_counter(redis: redis.Redis = Depends(get_redis)) -> ViewersCounter:
    yield ViewersCounter(redis)


@app.get("/viewers/{streamer_username}")
def viewers(
    streamer_username: str, viewers_counter: ViewersCounter = Depends(get_viewers_counter)
):
    return JSONResponse(
        status_code=200,
        content={"count": viewers_counter.get_viewers_count(streamer_username)},
    )


@app.get("/hls/{watch_key}/{file}")
def hls(
    request: Request,
    watch_key: str,
    file: str,
    streaming_keys: StreamingKeysService = Depends(get_streaming_keys),
    viewers_counter: ViewersCounter = Depends(get_viewers_counter),
):
    is_valid, streamer_username = streaming_keys.verify_watch_stream_key(watch_key)
    if not is_valid:
        return JSONResponse(status_code=403, content="Forbidden")
    else:
        rtmp_key = streaming_keys.get_streamer_key(streamer_username)
        path = Path(f"/tmp/hls/{rtmp_key}/{file}")
        if path.is_file():
            viewers_counter.add_viewer(streamer_username, request.client.host)
            return FileResponse(path)
        else:
            return JSONResponse(status_code=404, content="Not found")


@app.get("/auth_publish")
def root(name: str, streaming_keys: StreamingKeysService = Depends(get_streaming_keys)):
    """This endpoint is called by RTMP in nginx for authorization of streaming key"""
    is_valid = streaming_keys.verify_streamer_key(name)
    if is_valid:
        return {"message": "success"}
    else:
        return JSONResponse(status_code=403, content="Forbidden")
