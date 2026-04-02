#!/bin/bash

gcloud run deploy assignments-service \
  --source . \
  --region europe-west1 \
  --no-allow-unauthenticated

# URL=$(gcloud run services describe assignments-service --region europe-west1 --format='value(status.url)')

# gcloud run services update assignments-service --region europe-west1 --set-env-vars SERVICE_URL=$URL
