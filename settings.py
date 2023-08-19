import os
from re import escape
from string import ascii_letters, digits

SYMBOLS = ascii_letters + digits
PATTERN = rf'^[{escape(SYMBOLS)}]+$'
SHORT_LENGTH = 6
USER_SHORT_LENGTH = 16
MAX_URL_LENGTH = 1000
GENERATE_SHORT_RETRIES = 5
REDIRECT_VIEW = 'redirect_view'


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI',
        default='sqlite:///db.sqlite3'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv(
        'SECRET_KEY',
        default='SECRET_KEY'
    )
