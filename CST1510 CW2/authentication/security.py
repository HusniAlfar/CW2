import bcrypt
from hive_database.user import add_user, get_user, check_user_exists


def hash_password(password):
    """
    Turn a normal password into a secure hash using bcrypt.
    We do this to keep the password safe in the database.
    """
    password_bytes = password.encode("utf-8")  # change text to bytes
    salt = bcrypt.gensalt()                    # create random salt
    hashed = bcrypt.hashpw(password_bytes, salt)

    return hashed.decode("utf-8")              # store hash as string


def verify_password(password, hashed_password):
    """
    Check if the password the user typed matches the saved hash.
    Returns True or False.
    """
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def validate_username(username):
    """
    Check if the username format is correct.

    Simple rules:
    - cannot be empty
    - must be letters or numbers only
    - must be between 3 and 20 characters
    """
    if not username:
        return False, "Username cannot be empty"

    if not username.isalnum():
        return False, "Username must be letters and numbers only"

    if len(username) < 3 or len(username) > 20:
        return False, "Username must be 3–20 characters"

    return True, ""


def validate_password(password):
    """
    Check if the password is strong enough.

    Rules:
    - must be at least 6 characters
    - must have 1 uppercase letter
    - must have 1 lowercase letter
    - must have a number
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters"

    if not any(c.isupper() for c in password):
        return False, "Password must have an uppercase letter"

    if not any(c.islower() for c in password):
        return False, "Password must have a lowercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must have a number"

    return True, ""


def register_user(username, password, role):
    """
    Create a new user account.

    Steps:
    1. Check if the username already exists.
    2. Hash the password.
    3. Save the new user in the database.

    Returns:
    (True, user_id) if success,
    (False, message) if something is wrong.
    """
    if check_user_exists(username):
        return False, "Username already exists"

    hashed = hash_password(password)
    user_id = add_user(username, hashed, role)

    return True, user_id


def login_user(username, password):
    """
    Log in a user.

    Steps:
    1. Find the user in the database.
    2. Check the password.
    """
    user = get_user(username)

    if not user:
        return False, "Username not found"

    if verify_password(password, user["password_hash"]):
        return True, user

    return False, "Invalid password"
