import asyncio
import json
import logging
import signal
import sys
import redis.asyncio as aioredis
from app.config import settings
from app.services.indexer import repository_indexer

logger = logging.getLogger("repomind.worker")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

QUEUE_NAME = "repomind:indexing_queue"


async def dispatch_indexing_job(repository_id: str, job_id: str):
    """Enqueue indexing job into Redis queue, falling back to local async task if Redis is down."""
    try:
        r = aioredis.from_url(settings.REDIS_URL, socket_connect_timeout=1.5)
        payload = json.dumps({"repository_id": repository_id, "job_id": job_id})
        await r.rpush(QUEUE_NAME, payload)
        await r.aclose()
        logger.info(f"Enqueued indexing job {job_id} for repository {repository_id} to Redis")
    except Exception as e:
        logger.warning(f"Redis unavailable ({e}); dispatching indexing job {job_id} as in-process background task")
        asyncio.create_task(repository_indexer.index_repository(repository_id=repository_id, job_id=job_id))


async def run_worker():
    """Main worker loop pulling indexing jobs from Redis queue."""
    logger.info(f"Starting RepoMind background worker listening on Redis queue '{QUEUE_NAME}'...")
    running = True

    while running:
        try:
            r = aioredis.from_url(settings.REDIS_URL, socket_timeout=10, socket_keepalive=True)
            logger.info("Connected to Redis worker queue")
            while running:
                try:
                    result = await r.blpop([QUEUE_NAME], timeout=5)
                except (asyncio.TimeoutError, aioredis.TimeoutError):
                    continue

                if result:
                    _, raw_data = result
                    data = json.loads(raw_data.decode("utf-8"))
                    repo_id = data.get("repository_id")
                    job_id = data.get("job_id")
                    logger.info(f"Worker picked up job {job_id} for repo {repo_id}")
                    try:
                        await repository_indexer.index_repository(repository_id=repo_id, job_id=job_id)
                        logger.info(f"Worker successfully completed job {job_id}")
                    except Exception as exc:
                        logger.error(f"Worker failed processing job {job_id}: {exc}")
        except asyncio.CancelledError:
            running = False
            break
        except Exception as e:
            logger.warning(f"Worker connection issue: {e}. Reconnecting in 3s...")
            await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(run_worker())
