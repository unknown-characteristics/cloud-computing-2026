"""
Database credentials are stored as a single dotenv-formatted secret in Key Vault,
e.g.:
    db_user=...
    db_passwd=...
    db_connection_ip=mysql-flex.example.mysql.database.azure.com
    db_name=...
    db_port=3306
"""
from pydantic_settings import BaseSettings

from helpers.env_helper import init_env_from_str
from helpers.secrets import get_secret_data
from helpers.settings import settings


class Credentials(BaseSettings):
    db_user: str
    db_passwd: str
    db_connection_ip: str          # the Flex Server hostname
    db_name: str
    db_port: int = 3306


def _load() -> Credentials:
    raw = get_secret_data(settings.db_creds_secret)
    return init_env_from_str(raw, Credentials)


db_creds: Credentials = _load()
