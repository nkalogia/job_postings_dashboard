import os
import celery

BROKER_URL = os.environ.get("BROKER_URL")
RESULT_BACKEND_URL = os.environ.get("RESULT_BACKEND_URL")

app = celery.Celery(
    'skills',
    broker=BROKER_URL,
    backend=RESULT_BACKEND_URL,
    include=['skills']
)
