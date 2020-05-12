from authomatic import Authomatic
from authomatic.providers import oauth2

from root.utils import extract_secret, get_secrets

secrets = get_secrets()
oauth_secrets = extract_secret(secrets, "OAUTH")

OAUTH_CONFIG = {
    "facebook": {
        "id": 1,
        "class_": oauth2.Facebook,
        "consumer_key": extract_secret(oauth_secrets, "FACEBOOK_ID"),
        "consumer_secret": extract_secret(oauth_secrets, "FACEBOOK_SECRET"),
    },
    "github": {
        "id": 2,
        "class_": oauth2.GitHub,
        "access_headers": {"User-Agent": "VerdantFox"},
        "consumer_key": extract_secret(oauth_secrets, "GITHUB_ID"),
        "consumer_secret": extract_secret(oauth_secrets, "GITHUB_SECRET"),
    },
    "google": {
        "id": 3,
        "class_": oauth2.Google,
        "consumer_key": extract_secret(oauth_secrets, "GOOGLE_ID"),
        "consumer_secret": extract_secret(oauth_secrets, "GOOGLE_SECRET"),
        "scope": ["profile", "email"],
    },
}

# Instantiate Authomatic.
authomatic = Authomatic(
    OAUTH_CONFIG,
    extract_secret(oauth_secrets, "AUTHOMATIC_SECRET"),
    report_errors=extract_secret(oauth_secrets, "REPORT_ERRORS"),
)
