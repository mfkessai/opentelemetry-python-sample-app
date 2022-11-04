# OpenTelemetry sample FastAPI application on Cloud Run

This is a FastAPI sample application to check OpenTelemetry behavior on Money Forward Kessai use cases.
Intended to run on Google Cloud Run, but this would be helpful as an OpenTelemetry sample application for Python developers.

# How to develop

```sh
poetry install
poetry run uvicorn main:app --reload
```

# How to deploy

Before deploy, replace `{YOUR_PROJECT}` and `{GCR_DESTINATION}` in below command and application code with the name of GCP project that will actually run this application.

```sh
docker build -t gcr.io/{YOUR_PROJECT}/{GCR_DESTINATION}:latest --platform linux/amd64 .
docker push  gcr.io/{YOUR_PROJECT}/{GCR_DESTINATION}:latest
gcloud run deploy opentelemetry-fastapi-sample \
          --project {YOUR_PROJECT} \
          --region asia-northeast1 \
          --platform managed \
          --image gcr.io/{YOUR_PROJECT}/{GCR_DESTINATION}:latest \
          --memory 1024Mi \
          --max-instances 1 \
          --port 8000 \
          --allow-unauthenticated
```