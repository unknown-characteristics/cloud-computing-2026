from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from helpers.db_creds import db_creds

SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{db_creds.db_user}:{db_creds.db_passwd}"
    f"@{db_creds.db_connection_ip}:3306/{db_creds.db_name}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()