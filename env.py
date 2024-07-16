"""Yquando backend env keys & settings module."""

import os


def get_required_env(env_name: str) -> str:
    """Validate and return an environmental variable."""
    env_var = os.getenv(env_name)
    if env_var is None:
        error_message = f"{env_name} environmental variable not found."
        raise RuntimeError(error_message)
    return env_var


PG_HOST = get_required_env("PG_HOST")
PG_DATABASE = get_required_env("PG_DATABASE")
PG_USER = get_required_env("PG_USER")
PG_PASSWORD = get_required_env("PG_PASSWORD")

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
TWILIO_ACCOUNT_SID = get_required_env("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = get_required_env("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = get_required_env("TWILIO_NUMBER")

OPENAI_API_KEY = get_required_env("OPENAI_API_KEY")
