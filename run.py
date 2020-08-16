"""run.py

This is the main file called to run the flask application
"""
from src.factory import create_app

if __name__ == "__main__":

    app = create_app()

    # Localhost run
    app.run(host="0.0.0.0")
