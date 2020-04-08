from datetime import datetime
import time
import random
import string
import uuid


def valid_uuid(s):
    try:
        uuid.UUID(str(s))
        return True
    except ValueError:
        return False


def valid_email(email):
    if "@" not in email or "." not in email or email.index('@') > email.index('.'):
        return False
    return True


def valid_currency(currency_name):
    if len(currency_name) == 3 and currency_name.isupper():
        return True
    return False


def generate_email():
    return ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(5)) + "@future.comes"


def timestamp():
    return str(datetime.fromtimestamp(time.time()))
