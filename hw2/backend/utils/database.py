from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from utils.settings import Settings

settings = Settings()

engine = create_engine(settings.DB_URL, connect_args={"check_same_thread": False})

SessionGenerator = sessionmaker(engine)

def get_db():
    db = SessionGenerator()
    try:
        yield db
    finally:
        db.close()


Base = declarative_base()
