from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey


db = SQLAlchemy()


class LibraryModelMethods:
    """Mixin for library methods."""

    def save(cls) -> None:
        """Persist instance to the table."""
        db.session.add(cls)
        db.session.commit()

    def delete(cls) -> None:
        """Remove instance from the table."""
        db.session.delete(cls)
        db.session.commit()


class User(db.Model, LibraryModelMethods):
    """Model for users."""

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    book_limit = db.Column(db.Integer, default=3)
    checkouts = relationship("Checkout", backref="user")
    __table_args__ = (db.UniqueConstraint("firstname", "lastname", "email"),)


class Book(db.Model, LibraryModelMethods):
    """Model for books."""

    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    genre = db.Column(db.String, nullable=False)
    # Deleting a book will delete that book's checkout entry if it exists
    checkout = relationship("Checkout", cascade="all, delete, delete-orphan")


class Checkout(db.Model, LibraryModelMethods):
    """Model for checkouts - books that are checked out to a user."""

    book_id = db.Column(db.Integer, ForeignKey(Book.id), primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey(User.id), nullable=False)
    out_date = db.Column(db.DateTime, default=datetime.utcnow())
    due_date = db.Column(db.DateTime, nullable=False)
    book = relationship("Book", foreign_keys=[book_id])
