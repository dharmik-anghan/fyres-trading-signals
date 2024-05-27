import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    FYERS_ID = os.environ.get("FYERS_ID")
    TOTP_KEY = os.environ.get("TOTP_KEY")
    PIN = os.environ.get("PIN")
    CLIENT_ID = os.environ.get("CLIENT_ID")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    REDIRECT_URI = os.environ.get("REDIRECT_URI")
    ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
    RESPONSE_TYPE = os.environ.get("RESPONSE_TYPE")
    GRANT_TYPE = os.environ.get("GRANT_TYPE")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
    TELEGRAM_API_TOKEN = os.environ.get("TELEGRAM_API_TOKEN")
