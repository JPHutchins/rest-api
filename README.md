# Library REST API
An API for a library where users can checkout, return, and... destroy!?!? books.

# Installation / Development
A development server can be run in a Python virtual environment.

- `git clone https://github.com/JPHutchins/rest-api`
- `cd rest-api`
- `python3 -m venv venv` or `python -m venv venv` if `python` points at python3 
- `source venv/bin/activate`
- `pip install -r requirements.txt`

Everything should be ready to go but let's check by running `pytest`.  Provided tests should complete successfully.

You can now run the development server with the script `./run-dev-app`.
- The development server is on Flask default port 5000
- The server is accessible from external hosts (host=0.0.0.0). You can change this behavior by removing or changing the host argument given to `app.run()` in run.py.

# Interact
With the development server running you can send requests from curl, an API tool, or a browser.

The base url for every request will be `http://localhost:5000/library/v0.1`, eg. `http://localhost:5000/library/v0.1/checkouts`
- You may need to use "127.0.0.1" instead of "localhost"
- You will need to use the server's external IP address if you are accessing it from a different machine or VM, eg: "192.168.0.157"

When running in development mode the library comes prestocked with 4 users and 7 books.  Let's look at some endpoints - **remember to use the base url including port from above**.

- `GET /users` - get the list of users
  - `GET /users/{user_id}` - get details for a specific user by integer ID - (1-4 with only 4 users added)
    - `GET /users/{user_id}/checkouts` - get the list of checked out books for user
    - `POST /users/{user_id}/checkout/{book_id}` - checkout the book identified by book ID - (integer 1-7 with only 7 books in library)
    - `POST /users/{user_id}/return/{book_id}` - return a book to the library
- `GET /books` - get the list of books in the library
- `GET /checkouts` - get the list of current checked out books with soonest due dates first
- `DELETE /books/{book_id}` - remove a book from the library - this will also remove it from checkouts if it is checked out

# JSON Responses
users:
```
[
    {
        "book_limit": int,
        "books_checked_out": int,
        "email": str,
        "firstname": str,
        "lastname": str,
        "user_id": int,
    }
]
```
books:
```
[
    {
        "book_id": int,
        "genre": str,
        "title": str,
    }
]
```
checkouts:
```
[
    {
        "book_id": int,
        "due_date": str,
        "out_date": str,
        "title": str,
        "user_id": int,
    }
]
```




