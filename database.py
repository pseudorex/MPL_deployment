import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Use DATABASE_URL from environment variable (works for both local and Render)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:244901@localhost/newNormalized")

# If using Render, SSL is required
if "render.com" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"sslmode": "require"}  # Required for Render
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
