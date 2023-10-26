FROM python:3.11-bullseye

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app
ENV PYTHONPATH /app

RUN pip install --no-cache-dir --upgrade keyrings.google-artifactregistry-auth \
    google-cloud-secret-manager python-dateutil uvicorn[standard]

RUN pip install --no-cache-dir --upgrade \
    --extra-index-url https://europe-west4-python.pkg.dev/krules-dev-254113/krules-pre/simple \
    krules-core krules-env krules-subjects-storage-redis krules-dispatcher-cloudevents

ADD env.py /app/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]