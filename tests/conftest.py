"""Configure tests for library api."""
import pytest

from library import models


def add_users(db) -> None:
    """Add some users to the database."""
    users = [
        ("J.P.", "Hutchins", "jphutchins@gmail.com"),
        ("A", "AA", "A@AA.com"),
        ("B", "BB", "B@BB.com"),
        ("C", "CC", "C@CC.com"),
    ]
    for user in users:
        row = models.User()
        row.firstname = user[0]
        row.lastname = user[1]
        row.email = user[2]
        row.save()


def add_books(db) -> None:
    """Add some books to the database."""
    books = [
        ("Book A", "Genre A"),
        ("Book B", "Genre B"),
        ("Book C", "Genre C"),
        ("Book D", "Genre A"),
        ("Book E", "Genre A"),
        ("Book F", "Genre B"),
        ("Book G", "Genre A"),
    ]
    for book in books:
        row = models.Book()
        row.title = book[0]
        row.genre = book[1]
        row.save()
