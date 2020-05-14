"""Utility functions available throughout app"""
import os

import yaml

# Secrets path
CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "secrets.yaml")
)


def get_secrets():
    """Gets a secrets file at the specified path and setting"""

    if not os.path.exists(CONFIG_PATH):
        raise EnvironmentError(f"secrets file not found at: {CONFIG_PATH}")
    with open(CONFIG_PATH) as conf:
        secrets = yaml.safe_load(conf)

    # debug = os.environ.get("DEBUG")
    debug = True
    if debug:
        secrets = extract_secret(secrets, "DEV")
    else:
        secrets = extract_secret(secrets, "PROD")

    return secrets


def extract_secret(secrets, secret):
    try:
        return secrets[secret]
    except KeyError as e:
        raise EnvironmentError(
            f"YAML not set up properly. Missing {e}. "
            "To run in debug mode use DEBUG=1"
        )


def set_environment_variables(variables):
    for var, val in variables.items():
        os.environ[var] = val
