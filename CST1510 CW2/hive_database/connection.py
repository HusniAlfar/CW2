import sqlite3
from pathlib import Path

# This is the path where the database file will be stored
# I go two folders up, then into "DATA", then create "platform.db"
DB_PATH = Path(__file__).parent.parent / "DATA" / "platform.db"


def get_db_connection():
    """
    This function creates and returns a connection to the database.
    It also makes sure the DATA folder exists.
    """
    # Create the folder if it is not there
    DB_PATH.parent.mkdir(exist_ok=True)

    # Connect to the database file
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)

    # Make rows easier to access by column name
    conn.row_factory = sqlite3.Row

    return conn


def setup_database():
    """
    This function sets up the database.
    It runs another function that creates all tables.
    """
    # I import inside the function to avoid problems when the file loads
    from hive_database.tables import initialize_all_tables

    # Open the connection
    conn = get_db_connection()

    # Create all the tables in the database
    initialize_all_tables(conn)

    # Close the connection after finishing
    conn.close()




