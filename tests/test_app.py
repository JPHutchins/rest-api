from datetime import datetime
import json

from tests.conftest import API_BASE_PATH


def test_get_user_exists(client):
    response = client.get(f"{API_BASE_PATH}/users/1")
    data = json.loads(response.data)
    assert data["firstname"] == "J.P."
    assert data["lastname"] == "Hutchins"


def test_get_user_dne(client):
    response = client.get(f"{API_BASE_PATH}/users/99999")
    assert response.status_code == 400


def test_user_can_checkout_book(client):
    # User checkouts is empty
    response = client.get(f"{API_BASE_PATH}/users/1/checkouts")
    data = json.loads(response.data)
    assert data == []
    # Global checkouts is empty
    response = client.get(f"{API_BASE_PATH}/checkouts")
    data = json.loads(response.data)
    assert data == []
    # User checkout succeeds
    response = client.post(f"{API_BASE_PATH}/users/1/checkout/1")
    data = json.loads(response.data)
    assert "due_date" in data
    # User checkouts contains book
    response = client.get(f"{API_BASE_PATH}/users/1/checkouts")
    data = json.loads(response.data)
    assert data[0]["book_id"] == 1
    # Global checkouts contains book
    response = client.get(f"{API_BASE_PATH}/checkouts")
    data = json.loads(response.data)
    assert data[0]["book_id"] == 1
    assert data[0]["user_id"] == 1


def test_user_cannot_checkout_book_over_limit(client):
    client.post(f"{API_BASE_PATH}/users/1/checkout/1")
    client.post(f"{API_BASE_PATH}/users/1/checkout/2")
    client.post(f"{API_BASE_PATH}/users/1/checkout/3")
    response = client.get(f"{API_BASE_PATH}/users/1")
    data = json.loads(response.data)
    assert data["book_limit"] == 3  # default book limit
    assert data["books_checked_out"] == 3
    # Try to checkout 4th book
    response = client.post(f"{API_BASE_PATH}/users/1/checkout/4")
    assert response.status_code == 400
    # Check that state is the same as before
    response = client.get(f"{API_BASE_PATH}/users/1")
    data = json.loads(response.data)
    assert data["book_limit"] == 3  # default book limit
    assert data["books_checked_out"] == 3
    # Check that book 4 is not checked out
    response = client.get(f"{API_BASE_PATH}/checkouts")
    data = json.loads(response.data)
    for checkout in data:
        assert checkout["book_id"] != 4


def test_user_cannot_checkout_book_that_is_checked_out(client):
    client.post(f"{API_BASE_PATH}/users/1/checkout/1")
    # Try to checkout same book
    response = client.post(f"{API_BASE_PATH}/users/1/checkout/1")
    assert response.status_code == 400
    # Another user tries to checkout User 1's checkout
    response = client.post(f"{API_BASE_PATH}/users/2/checkout/1")
    assert response.status_code == 400


def test_user_can_return_book(client):
    client.post(f"{API_BASE_PATH}/users/1/checkout/1")
    response = client.get(f"{API_BASE_PATH}/users/1")
    data = json.loads(response.data)
    assert data["books_checked_out"] == 1
    # Return book
    response = client.post(f"{API_BASE_PATH}/users/1/return/1")
    data = json.loads(response.data)
    assert data["message"] == "success"
    # Check that user has no checkouts
    response = client.get(f"{API_BASE_PATH}/users/1")
    data = json.loads(response.data)
    assert data["books_checked_out"] == 0
    # Global checkouts is empty
    response = client.get(f"{API_BASE_PATH}/checkouts")
    data = json.loads(response.data)
    assert data == []


def test_get_checkouts_ordered_by_due_date(client):
    client.post(f"{API_BASE_PATH}/users/1/checkout/1")
    client.post(f"{API_BASE_PATH}/users/3/checkout/2")
    client.post(f"{API_BASE_PATH}/users/1/checkout/3")
    client.post(f"{API_BASE_PATH}/users/2/checkout/4")
    client.post(f"{API_BASE_PATH}/users/3/checkout/5")
    client.post(f"{API_BASE_PATH}/users/4/checkout/6")
    response = client.get(f"{API_BASE_PATH}/checkouts")
    data = json.loads(response.data)
    previous_due_date = datetime.fromisocalendar(3000, 1, 1)
    for checkout in data:
        assert previous_due_date > datetime.strptime(
            checkout["due_date"], "%a, %d %b %Y %H:%M:%S %Z"
        )


def test_delete_book(client):
    response = client.get(f"{API_BASE_PATH}/books")
    data = json.loads(response.data)
    assert len(data) == 7
    # Delete book
    response = client.delete(f"{API_BASE_PATH}/books/1")
    assert response.status_code == 200
    # Check that book is gone
    response = client.get(f"{API_BASE_PATH}/books")
    data = json.loads(response.data)
    assert len(data) == 6
    for book in data:
        assert book["book_id"] != 1
    # Try to delete book that DNE
    response = client.delete(f"{API_BASE_PATH}/books/1")
    assert response.status_code == 400


def test_delete_book_removes_from_checkout(client):
    client.post(f"{API_BASE_PATH}/users/1/checkout/1")
    # User checkouts contains book
    response = client.get(f"{API_BASE_PATH}/users/1/checkouts")
    data = json.loads(response.data)
    assert data[0]["book_id"] == 1
    # Global checkouts contains book
    response = client.get(f"{API_BASE_PATH}/checkouts")
    data = json.loads(response.data)
    assert data[0]["book_id"] == 1
    assert data[0]["user_id"] == 1
    # Delete book
    response = client.delete(f"{API_BASE_PATH}/books/1")
    assert response.status_code == 200
    # Check that user has no checkouts
    response = client.get(f"{API_BASE_PATH}/users/1")
    data = json.loads(response.data)
    assert data["books_checked_out"] == 0
    # Global checkouts is empty
    response = client.get(f"{API_BASE_PATH}/checkouts")
    data = json.loads(response.data)
    assert data == []
