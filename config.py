"""Define Flask configurations."""
import os


class Config:
    """Base config variables."""

    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(Config):
    """Config variables for development."""

    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"  # in-memory database


class ProdConfig(Config):
    """Config variables for production."""

    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
