from email_validator import validate_email, EmailNotValidError

def is_valid_email(email):
    try:
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError as e:
        return False
