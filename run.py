"""run.py

This is the main file called to run the flask application
"""
import os

from root.factory import create_app, get_config


if __name__ == "__main__":
    config_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "config.yaml")
    )
    app = create_app(config=get_config(config_path))
    app.run(host="0.0.0.0")
