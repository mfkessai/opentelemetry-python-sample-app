# OpenTelemetry sample FastAPI application on Cloud Run

This is a flask application to check OpenTelemetry behavior on Money Forward Kessai use cases.
Intended to run on Google Cloud Functions, but this would be helpful as an OpenTelemetry sample application for Python developers.

# How to develop

```sh
virtualenv .venv
. .venv/bin/activate
pip install -r requirements.txt      
python main.py
```

# How to deploy

Before deploy, replace `{YOUR_PROJECT}`  in below command and application code with the name of GCP project that will actually run this application.

```sh
gcloud functions deploy opentelemetry-flask-sample \
          --entry-point handler \
          --runtime python310 \
          --trigger-http \
          --project {YOUR_PROJECT} \
          --region asia-northeast1 \
          --allow-unauthenticated
```
