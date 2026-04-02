from pydantic_settings import BaseSettings, SettingsConfigDict
from helpers.env_helper import init_env_from_str
from helpers.secrets import get_secret_data

class Credentials(BaseSettings):
    db_user: str
    db_passwd: str
    db_connection_ip: str
    db_name: str

    # Tell Pydantic to read from the .env file
    # model_config = SettingsConfigDict(env_file="db.env", env_file_encoding="utf-8")

creds_data = get_secret_data("USERS_DB_CREDS")
db_creds = init_env_from_str(creds_data, Credentials)
