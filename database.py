from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:244901@localhost/newNormalized'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
# import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
#
# # ✅ Get database URL from environment variable
# db_url = os.environ.get("DATABASE_URL")
#
# # ✅ Convert old prefix (postgres://) to the one SQLAlchemy expects
# if db_url and db_url.startswith("postgres://"):
#     db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
#
# # ✅ Create SQLAlchemy engine with SSL (Render/Heroku usually require this)
# engine = create_engine(
#     db_url,
#     connect_args={"sslmode": "require"}  # remove if your DB doesn’t need SSL
# )
#
# # ✅ Create session factory
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# # ✅ Base class for models
# Base = declarative_base()
#
