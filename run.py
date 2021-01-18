"""Run a development server."""
import os

from library import create_app


app = create_app(f"config.{os.environ.get('FLASK_CONFIG')}")

if __name__ == "__main__":
    app.run(host="0.0.0.0")
