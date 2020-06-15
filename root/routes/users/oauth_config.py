"""Authomatic Oauth configuration file

Pull secret ids and keys from environment variables set in .env
"""

import os

from authomatic import Authomatic
from authomatic.providers import oauth2

OAUTH_CONFIG = {
    "Facebook": {
        "id": 1,
        "class_": oauth2.Facebook,
        "consumer_key": os.getenv("FACEBOOK_ID"),
        "consumer_secret": os.getenv("FACEBOOK_SECRET"),
    },
    "Google": {
        "id": 1,
        "class_": oauth2.Google,
        "consumer_key": os.getenv("GOOGLE_ID"),
        "consumer_secret": os.getenv("GOOGLE_SECRET"),
        # Google requires a scope be specified to work properly
        "scope": ["profile", "email"],
    },
    "GitHub": {
        "id": 3,
        "class_": oauth2.GitHub,
        # GitHub requires a special header to work properly
        "access_headers": {"User-Agent": "VerdantFox"},
        "consumer_key": os.getenv("GITHUB_ID"),
        "consumer_secret": os.getenv("GITHUB_SECRET"),
    },
}

report_errors = (
    True if os.getenv("REPORT_ERRORS", "0").lower() in ("1", "true") else False
)

# Instantiate Authomatic.
authomatic = Authomatic(
    OAUTH_CONFIG, os.getenv("AUTHOMATIC_SECRET"), report_errors=report_errors,
)
