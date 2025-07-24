# utils.py

from dotenv import load_dotenv
import os

load_dotenv(override=True)

def get_env_var(key):
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Missing environment variable: {key}")
    return value.strip().strip('"').strip("'")
