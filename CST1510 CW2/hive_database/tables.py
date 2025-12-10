def create_users_table(conn):
    """
    Create the users table.

    This table is for login / authentication.
    It will only be created if it does not exist.
    """
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,   -- unique id for each user
            username TEXT NOT NULL UNIQUE,          -- username must be unique
            password_hash TEXT NOT NULL,            -- saved password in hash form
            role TEXT NOT NULL                      -- user role, for example: admin or analyst
        )
    """)

    # Save the changes to the database
    conn.commit()


def create_cyber_incidents_table(conn):
    """
    Create the cyber_incidents table.

    This table stores information about cyber security incidents.
    """
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cyber_incidents (
            incident_id INTEGER PRIMARY KEY,   -- id of the incident
            timestamp TEXT NOT NULL,           -- when the incident happened
            severity TEXT NOT NULL,            -- how serious it is (low, medium, high)
            category TEXT NOT NULL,            -- type of incident (malware, phishing, etc.)
            status TEXT NOT NULL,              -- current status (open, closed, in_progress)
            description TEXT                   -- extra details about the incident
        )
    """)

    conn.commit()


def create_datasets_table(conn):
    """
    Create the datasets_metadata table.

    This table keeps info about datasets we upload.
    """
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS datasets_metadata (
            dataset_id INTEGER PRIMARY KEY,    -- id of the dataset
            name TEXT NOT NULL,               -- name of the dataset
            rows INTEGER NOT NULL,            -- how many rows
            columns INTEGER NOT NULL,         -- how many columns
            uploaded_by TEXT NOT NULL,        -- who uploaded it
            upload_date TEXT NOT NULL         -- when it was uploaded
        )
    """)

    conn.commit()


def create_tickets_table(conn):
    """
    Create the it_tickets table.

    This table stores IT support tickets.
    """
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS it_tickets (
            ticket_id INTEGER PRIMARY KEY,     -- id of the ticket
            priority TEXT NOT NULL,           -- priority (low, medium, high)
            description TEXT NOT NULL,        -- what the problem is
            status TEXT NOT NULL,             -- status (open, in_progress, closed)
            assigned_to TEXT NOT NULL,        -- who is working on it
            created_at TEXT NOT NULL,         -- when the ticket was created
            resolution_time_hours REAL        -- how many hours it took to fix
        )
    """)

    conn.commit()


def initialize_all_tables(conn):
    """
    Create all tables in the database.

    This function calls the other functions above.
    """
    create_users_table(conn)
    create_cyber_incidents_table(conn)
    create_datasets_table(conn)
    create_tickets_table(conn)
