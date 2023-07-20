from celery import Celery
import os

app = Celery('tasks',
             broker=os.environ["SUBJECTS_REDIS_URL"],  # TODO: use specific env var
             result_backend = f"db+postgresql://{os.environ['SQL_USERNAME']}:{os.environ['SQL_PASSWORD']}@{os.environ['SQL_ADDRESS']}/{os.environ['SQL_DATABASE']}"
             )

@app.task
def add(x, y):
    return x + y