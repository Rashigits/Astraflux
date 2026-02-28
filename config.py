import os
from cryptography.fernet import Fernet

from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")



GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

FERNET_KEY = os.getenv("FERNET_KEY")
cipher = Fernet(FERNET_KEY.encode())

DATABASE = "astraflux.db"
SESSION_EXPIRY = int(os.getenv("SESSION_EXPIRY", 86400))
