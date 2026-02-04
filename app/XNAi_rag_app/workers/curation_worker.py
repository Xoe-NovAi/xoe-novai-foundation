#!/usr/bin/env python3
# Xoe-NovAi Curation Worker
# Guide Ref: Section 8.2 (Pattern: Redis Job Queue Processing)
import os
import time
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import redis
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# --- Config ---
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
QUEUE_KEY = os.getenv("QUEUE_KEY", "curation_queue")
JOB_PREFIX = os.getenv("JOB_PREFIX", "curation:")
LOG_DIR = Path(os.getenv("LOG_DIR", "/app/logs/curations"))
DATA_DIR = Path(os.getenv("DATA_DIR", "/app/data/curations"))
MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS", "3"))
WORKER_NAME = os.getenv("WORKER_NAME", "curation-worker-1")

LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
	level=logging.INFO,
	format='{"time":"%(asctime)s","worker":"%(name)s","level":"%(levelname)s","msg":"%(message)s"}',
	handlers=[logging.FileHandler(LOG_DIR / f"{WORKER_NAME}.log"), logging.StreamHandler()]
)
logger = logging.getLogger(WORKER_NAME)

# --- Redis connection ---
@retry(stop=stop_after_attempt(5), wait=wait_exponential(min=1, max=30),
	retry=retry_if_exception_type(redis.ConnectionError))
def connect_redis() -> redis.Redis:
    logger.info(f"Connecting to Redis at {REDIS_HOST}:{REDIS_PORT}...")
    client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        db=REDIS_DB,
        decode_responses=True
    )
    client.ping()
    return client

rdb = connect_redis()

def get_job_data(job_id: str) -> dict:
	return rdb.hgetall(job_id)

def update_job_status(job_id: str, status: str, extra: dict = {}):
	update = {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}
	if extra:
		update.update(extra)
	rdb.hset(job_id, mapping=update)
	logger.info(f"{job_id} status -> {status}")

def run_subprocess(job_id: str, command: list[str]):
	log_path = DATA_DIR / f"{job_id.replace(':', '_')}.log"
	with open(log_path, "w") as out:
		proc = subprocess.Popen(command, stdout=out, stderr=subprocess.STDOUT)
		proc.wait()
		return proc.returncode

def process_job(job_id: str):
	meta = get_job_data(job_id)
	if not meta:
		logger.warning(f"No metadata for {job_id}")
		return

	attempts = int(meta.get("attempts", 0))
	if attempts >= MAX_ATTEMPTS:
		update_job_status(job_id, "failed", {"error": "max_attempts_reached"})
		return

	update_job_status(job_id, "processing", {"attempts": str(attempts + 1)})

	source = meta.get("source", "unknown")
	category = meta.get("category", "misc")
	query = meta.get("query", "")
	# Updated path to crawl.py and correct arguments (--curate instead of --source)
	cmd = ["python3", "/app/XNAi_rag_app/workers/crawl.py", "--curate", source, "--category", category, "--query", query]

	try:
		ret = run_subprocess(job_id, cmd)
		if ret == 0:
			update_job_status(job_id, "completed")
		else:
			update_job_status(job_id, "failed", {"error": f"Exit {ret}"})
	except Exception as e:
		update_job_status(job_id, "failed", {"error": str(e)})

def main():
	logger.info(f"{WORKER_NAME} started, listening on {QUEUE_KEY}")
	while True:
		try:
			job = rdb.blpop([QUEUE_KEY], timeout=5)
			if not job:
				time.sleep(1)
				continue
			job_id = job[1]
			process_job(job_id)
		except redis.ConnectionError as e:
			logger.error(f"Redis connection lost: {e}")
			time.sleep(5)

if __name__ == "__main__":
    main()
