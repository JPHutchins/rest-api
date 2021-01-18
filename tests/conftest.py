"""Configure tests for library api."""
import pytest

from library import models, const
from library.models import db


API_BASE_PATH = f"/{const.API_NAME}/{const.API_VERSION}"


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


@pytest.fixture
def app():
    from library import create_app

    app = create_app("config.DevConfig")
    with app.app_context():
        db.init_app(app)
        db.create_all()
        add_users(db)
        add_books(db)

    yield app


@pytest.fixture
def client(app):
    return app.test_client()
