"""
Azure Key Vault wrapper.

In production, the App Service has a system-assigned Managed Identity that has
been granted `Key Vault Secrets User` on the vault. DefaultAzureCredential picks
that identity automatically. Locally it falls back to:
  1. environment variables (AZURE_CLIENT_ID / AZURE_CLIENT_SECRET / AZURE_TENANT_ID)
  2. `az login` user
so no code change is needed between environments.
"""
from functools import lru_cache
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from helpers.settings import settings


@lru_cache(maxsize=1)
def _client() -> SecretClient:
    return SecretClient(
        vault_url=settings.key_vault_url,
        credential=DefaultAzureCredential(),
    )


@lru_cache(maxsize=64)
def get_secret_data(secret_id: str) -> str:
    """Fetch the latest version of a Key Vault secret as a UTF-8 string."""
    return _client().get_secret(secret_id).value
