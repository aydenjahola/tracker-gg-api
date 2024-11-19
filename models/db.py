from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
import os

load_dotenv()


Base = declarative_base()


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, unique=True, nullable=False)
    user = Column(String, nullable=False)
    permission = Column(String, default="normal")
    created_at = Column(DateTime, default=func.now(), nullable=False)


DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True, future=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_db() -> None:
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)


def add_api_key(
    db: Session, api_key: str, user: str, permission: str = "normal"
) -> APIKey:
    """
    Function to insert a new API key into the database.
    Ensures the key is unique.

    Args:
        db: The SQLAlchemy session.
        api_key: The API key to add.
        user: The associated user for the API key.
        permission: The permission level for the API key ('normal' or 'admin').

    Returns:
        The created APIKey object.

    Raises:
        Exception: If the API key already exists in the database.
    """
    db_api_key = APIKey(key=api_key, user=user, permission=permission)
    db.add(db_api_key)
    try:
        db.commit()

    except IntegrityError as e:
        db.rollback()

        raise Exception(f"API Key '{api_key}' already exists in the database.") from e
    return db_api_key
