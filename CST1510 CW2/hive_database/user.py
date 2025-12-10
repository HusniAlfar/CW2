from hive_database.connection import get_db_connection


def add_user(username, password_hash, role):
    """
    Add a new user to the database.

    This function saves a username, password hash, and role.
    It returns the new user's id.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert the new user into the table
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role)
    )

    conn.commit()

    # Get the ID of the new user
    user_id = cursor.lastrowid

    conn.close()
    return user_id


def get_user(username):
    """
    Get a user by username.

    This returns one row from the database.
    If the user does not exist, it returns None.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Select the user with the given username
    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()

    conn.close()
    return user


def check_user_exists(username):
    """
    Check if a username already exists in the database.

    Returns True if the username is found.
    Returns False if not found.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    )

    # If fetchone gives a row, the user exists
    exists = cursor.fetchone() is not None

    conn.close()
    return exists
