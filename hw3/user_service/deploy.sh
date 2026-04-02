gcloud run deploy users-service \
  --source . \
  --region europe-west1 \
  --no-allow-unauthenticated

URL=$(gcloud run services describe users-service --region europe-west1 --format='value(status.url)')

gcloud run services update users-service --region europe-west1 --set-env-vars SERVICE_URL=$URL
