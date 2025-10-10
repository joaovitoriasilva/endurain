import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine.url import URL

# Define the database connection URL using environment variables
db_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.environ.get("DB_USER", "endurain"),
    password=os.environ.get("DB_PASSWORD"),
    host=os.environ.get("DB_HOST", "postgres"),
    port=os.environ.get("DB_PORT", "5432"),
    database=os.environ.get("DB_DATABASE", "endurain"),
)

# Create the SQLAlchemy engine
engine = create_engine(
    db_url, pool_size=10, max_overflow=20, pool_timeout=180, pool_recycle=3600
)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()


def get_db():
    """
    Yields a new SQLAlchemy database session.

    This generator function creates a new database session using SessionLocal,
    yields it for use in database operations, and ensures the session is properly
    closed after use. Intended for use as a dependency in FastAPI routes or other
    contexts where session management is required.

    Yields:
        Session: An active SQLAlchemy database session.

    Example:
        with get_db() as db:
            # use db session here
    """
    # Create a new database session and return it
    db = SessionLocal()

    try:
        # Yield the database session
        yield db
    finally:
        # Close the database session
        db.close()
