from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from helpers.settings import settings

SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{settings.db_user}:{settings.db_passwd}"
    f"@{settings.db_connection_ip}:3306/{settings.db_name}"
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