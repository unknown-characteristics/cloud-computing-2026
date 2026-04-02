from google.cloud import secretmanager
from helpers.settings import settings

def get_secret_data(secret_id):
    client = secretmanager.SecretManagerServiceClient()

    name = f"projects/{settings.project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})

    # Return the decoded payload.
    return response.payload.data.decode("UTF-8")
