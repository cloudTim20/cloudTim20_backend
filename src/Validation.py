from datetime import datetime

def validate_datetime(date_str):
    try:
        datetime.strptime(date_str, '%d-%m-%Y')
        return True
    except ValueError:
        return False


def validate_email(email):
    if '@' in email:
        return True
    return False


def validate_length(s, min_length, max_length):
    if len(s) < min_length or len(s) > max_length:
        return False
    return True