import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("MONGODB_HOST")
DB_USER = os.getenv("MONGODB_USER")
DB_PASS = os.getenv("MONGODB_PASS")
DB_CLUSTER = os.getenv("MONGODB_CLUSTER")

# OAuth2 configuration
OAUTH2_CLIENT_ID = os.getenv("OAUTH2_CLIENT_ID")
OAUTH2_CLIENT_SECRET = os.getenv("OAUTH2_CLIENT_SECRET")
OAUTH2_REDIRECT_URI = "http://localhost:5000/callback"

FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
PUBLIC_ALL = os.getenv("PUBLIC_ALL", False)

HOST = os.getenv("HOST", "0.0.0.0")
PORT = os.getenv("PORT", 5000)
DEBUG = os.getenv("DEBUG", False)
