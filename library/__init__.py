"""Define the API for library."""
import os
from datetime import datetime, timedelta

from flask import Flask, jsonify

from library import const, models
from tests.conftest import add_books, add_users


API_BASE_PATH = f"/{const.API_NAME}/{const.API_VERSION}"
TESTING = os.environ.get("FLASK_CONFIG") == "DevConfig"


def create_app(config) -> Flask:
    """Create, configure and return instance of the application."""
    app = Flask(__name__)
    app.config.from_object(config)

    with app.app_context():
        from library.models import db

        db.init_app(app)
        db.create_all()

        if TESTING:
            add_users(db)
            add_books(db)

        @app.route(f"{API_BASE_PATH}/users", methods=["GET"])
        def users():
            """Get the list of users."""
            users = db.session.query(models.User).all()
            users_json = [
                {
                    "book_limit": user.book_limit,
                    "books_checked_out": len(user.checkouts),
                    "email": user.email,
                    "firstname": user.firstname,
                    "lastname": user.lastname,
                    "uri": f"/users/{user.id}",
                }
                for user in users
            ]
            return jsonify(users_json)

        @app.route(f"{API_BASE_PATH}/users/<int:user_id>", methods=["GET"])
        def user(user_id: int = None):
            """Get the user by id."""
            user = db.session.query(models.User).filter_by(id=user_id).first()
            if not user:
                return jsonify({"error": f"User {user_id} does not exist."}), 400
            user_info = {
                "book_limit": user.book_limit,
                "books_checked_out": len(user.checkouts),
                "email": user.email,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "checkouts": [
                    {"book_id": checkout.book_id, "due_date": checkout.due_date}
                    for checkout in user.checkouts
                ],
            }
            return jsonify(user_info)

        @app.route(f"{API_BASE_PATH}/users/<int:user_id>/checkouts", methods=["GET"])
        def user_checkouts(user_id: int = None):
            """Get the list of books checked out by a user."""
            user = db.session.query(models.User).filter_by(id=user_id).first()
            if not user:
                return jsonify({"error": f"User {user_id} does not exist."}), 400
            checkouts_json = [
                {
                    "book_id": checkout.book_id,
                    "out_date": checkout.out_date,
                    "due_date": checkout.due_date,
                    "title": checkout.book.title,
                }
                for checkout in user.checkouts
            ]
            return jsonify(checkouts_json)

        @app.route(
            f"{API_BASE_PATH}/users/<int:user_id>/checkout/<int:book_id>",
            methods=["POST"],
        )
        def checkout_book(
            user_id: int, book_id: int, days: int = const.DEFAULT_CHECKOUT_TIME
        ):
            """Checkout the book to user if possible."""
            user = db.session.query(models.User).filter_by(id=user_id).first()
            if not user:
                return jsonify({"error": f"User {user_id} does not exist."}), 400
            if user.book_limit <= len(user.checkouts):
                response = jsonify(
                    {"error": f"User has reached checkout limit of {user.book_limit}"}
                )
                return response, 400
            book = db.session.query(models.Book).filter_by(id=book_id).first()
            if not book:
                return jsonify({"error": f"Book {book_id} does not exist."}), 400
            if len(book.checkout) > 0:
                response = jsonify({"error": f"Book {book_id} is already checked out."})
                return response, 400

            checkout = models.Checkout()
            checkout.book_id = book_id
            checkout.user_id = user_id
            checkout.out_date = datetime.utcnow()
            checkout.due_date = checkout.out_date + timedelta(days=13)
            checkout.save()

            response = jsonify({"due_date": checkout.due_date})
            response.status_code = 201
            response.headers["Location"] = f"{API_BASE_PATH}/users/{user_id}/checkouts"
            return response

        @app.route(f"{API_BASE_PATH}/books", methods=["GET"])
        def books():
            """Get the list of books in the library."""
            books = db.session.query(models.Book).all()
            return jsonify(
                [
                    {
                        "book_id": book.id,
                        "genre": book.genre,
                        "title": book.title,
                    }
                    for book in books
                ]
            )

        @app.route(f"{API_BASE_PATH}/books/<int:book_id>", methods=["DELETE"])
        def delete_book(book_id: int):
            """Delete the book by id if possible."""
            book = db.session.query(models.Book).filter_by(id=book_id).first()
            if book is None:
                return jsonify({"error": f"Book {book_id} does not exist."}), 400
            book.delete()
            return jsonify({"message": f"Book {book_id} removed."})

        @app.route(
            f"{API_BASE_PATH}/users/<int:user_id>/return/<int:book_id>",
            methods=["POST"],
        )
        def return_book(user_id: int, book_id: int):
            """Return the book checked out by user, if possible."""
            user = db.session.query(models.User).filter_by(id=user_id).first()
            if not user:
                return jsonify({"error": f"User {user_id} does not exist."}), 400
            for checkout in user.checkouts:
                if checkout.book_id == book_id:
                    db.session.query(models.Checkout).filter_by(book_id=book_id).delete(
                        synchronize_session="fetch"
                    )
                    db.session.commit()
                    response = jsonify({"message": "success"})
                    response.headers[
                        "Location"
                    ] = f"{API_BASE_PATH}/users/{user_id}/checkouts"
                    return response
            response = jsonify(
                {"error": f"User {user_id} has not checked out Book {book_id}."}
            )
            return response, 400

        @app.route(f"{API_BASE_PATH}/checkouts", methods=["GET"])
        def checkouts():
            """Get the list of books currently checked out."""
            checkouts = (
                db.session.query(models.Checkout)
                .order_by(models.Checkout.due_date)
                .all()
            )
            checkouts_json = [
                {
                    "book_id": checkout.book_id,
                    "due_date": checkout.due_date,
                    "out_date": checkout.out_date,
                    "title": checkout.book.title,
                    "user_id": checkout.user_id,
                }
                for checkout in checkouts
            ]
            return jsonify(checkouts_json)

        return app
