"""
Database configuration module.

PUBLIC_INTERFACE
Provides SQLAlchemy session factory and declarative base that can be imported
across the application.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./tic_tac_toe.db"

# `check_same_thread=False` is required only for SQLite.
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
