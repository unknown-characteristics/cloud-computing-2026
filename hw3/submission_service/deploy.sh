#!/bin/bash

# Numele proiectului si regiunea (ajusteaza daca folosești o alta)
PROJECT_ID="cloudcomputing-491711"
REGION="europe-west1"
SERVICE_NAME="submission-service"

# Face deploy la containerul Docker în Cloud Run
gcloud run deploy $SERVICE_NAME \
  --source . \
  --region $REGION \
  --project $PROJECT_ID \
  --allow-unauthenticated \
  --set-env-vars FIRESTORE_PROJECT_ID=$PROJECT_ID,PUBSUB_TOPIC="submission-events"

echo "Deployed successfully!"