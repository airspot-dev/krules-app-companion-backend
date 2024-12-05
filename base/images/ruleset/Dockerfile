FROM python:3.11-bullseye

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ADD ./app /app

WORKDIR /app
ENV PYTHONPATH /app


RUN pip install --no-cache-dir --upgrade \
    google-cloud-secret-manager

RUN pip install --no-cache-dir "krules-framework[redis,pubsub,fastapi]==1.1.0"

# development libs
RUN pip install --no-cache-dir pysnooper ipython


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]