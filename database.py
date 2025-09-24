# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
#
# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:244901@localhost/newNormalized'
#
# engine = create_engine(SQLALCHEMY_DATABASE_URL)
#
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# Base = declarative_base()

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Get database URL from environment variable
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL")

# Create SQLAlchemy engine with SSL (required for many remote Postgres)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"sslmode": "require"}  # add this if your DB requires SSL
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
