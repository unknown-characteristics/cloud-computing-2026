#!/bin/bash

gcloud run deploy submissions-service \
  --source . \
  --region europe-west1 \
  --no-allow-unauthenticated \
  --set-env-vars PROJECT_ID=cloudcomputing-491711,PUBSUB_TOPIC=submissions-events

echo "Deployed successfully!"
