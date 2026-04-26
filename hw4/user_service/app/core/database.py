"""
Azure Database for MySQL — Flexible Server connection.

Differences vs. Cloud SQL:
- Uses TCP (no unix socket).
- SSL is enforced by default on Flex Server. We point pymysql at the system
  CA bundle (`/etc/ssl/certs/ca-certificates.crt` on Debian-based images),
  which already contains every DigiCert root Azure currently uses
  (Global Root CA and Global Root G2). Override with DB_SSL_CA_PATH if you
  ship a single-cert PEM in a different location.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from helpers.db_creds import db_creds

DB_SSL_CA_PATH = os.environ.get(
    "DB_SSL_CA_PATH", "/etc/ssl/certs/ca-certificates.crt"
)

SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{db_creds.db_user}:{db_creds.db_passwd}"
    f"@{db_creds.db_connection_ip}:{db_creds.db_port}/{db_creds.db_name}"
)

connect_args = {}
if os.path.isfile(DB_SSL_CA_PATH):
    connect_args["ssl"] = {"ca": DB_SSL_CA_PATH}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
    connect_args=connect_args,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables. Call this from a startup hook, NOT at import time —
    otherwise an unreachable DB blocks app startup and Azure kills the
    container with ContainerTimeout."""
    # Importing models here ensures they are registered on Base.metadata.
    from model import user_model, outbox, other_event  # noqa: F401
    Base.metadata.create_all(bind=engine)
