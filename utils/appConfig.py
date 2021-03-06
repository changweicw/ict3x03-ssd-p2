import sys
import os
from dotenv import load_dotenv
import distutils.util

load_dotenv()


class DefaultConfig:
    """Default Configuration"""
    MYSQL_HOST = os.getenv('MYSQL_HOST')
    MYSQL_USER = os.getenv('MYSQL_USER')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    MYSQL_DB = os.getenv('MYSQL_DB')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT'))
    MYSQL_CURSORCLASS = os.getenv('MYSQL_CURSORCLASS')
    SECRET_KEY = os.getenv('SECRET_KEY')
    GOOGLE_BUCKET_ID = os.getenv('GOOGLE_BUCKET_ID')
    GOOGLE_BUCKET_URL = os.getenv('GOOGLE_BUCKET_URL')
    GOOGLE_BUCKET_JSON_PATH = os.getenv('GOOGLE_BUCKET_JSON')
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "bucket_key.json"
    ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS').split(",")
    TEMP_UPLOAD_FOLDER_NAME = os.getenv('TEMP_UPLOAD_FOLDER_NAME')
    GMAIL_ID = os.getenv('GMAIL_ID')
    GMAIL_PW = os.getenv('GMAIL_PW')
    LOGIN_TEMPLATE_FILENAME = os.getenv('LOGIN_TEMPLATE_FILENAME')
    RESET_TEMPLATE_FILENAME = os.getenv('RESET_TEMPLATE_FILENAME')
    LOGIN_EMAIL_TITLE = os.getenv('LOGIN_EMAIL_TITLE')
    RESET_EMAIL_TITLE = os.getenv('RESET_EMAIL_TITLE')
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORTS = os.getenv('SMTP_PORTS').split(',')
    LOGGING_FOLDER = os.getenv('LOGGING_FOLDER')
    SESSION_TIMEOUT = os.getenv('SESSION_TIMEOUT')
    TESTING = bool(distutils.util.strtobool(os.getenv('TESTING')))
    LOGING_DISABLED = os.getenv('LOGIN_DISABLED')
    REMEMBER_ME_TIMEOUT_DAYS = os.getenv('REMEMBER_ME_TIMEOUT_DAYS')
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

    SERVER_IP = os.getenv('SERVER_IP')
    SERVER_PORT = os.getenv('SERVER_PORT')

    ACCOUNT_LOCOKOUT_MINUTES = int(os.getenv('ACCOUNT_LOCKOUT_MINUTES'))

    PASSWORD_COMMON_FILENAME = os.getenv('PASSWORD_COMMON_FILENAME')

    RECAPTCHA_USE_SSL = os.getenv('RECAPTCHA_USE_SSL')
    RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY')
    RECAPTCHA_OPTIONS = {'theme': 'black'}
