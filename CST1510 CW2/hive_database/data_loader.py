import pandas as pd
from pathlib import Path
from hive_database.connection import get_db_connection

# Base folder for data files
DATA_DIR = Path(__file__).parent.parent / "DATA"

# Paths to CSV backup files
CYBER_CSV = DATA_DIR / "cyber_incidents.csv"
DATASETS_CSV = DATA_DIR / "datasets_metadata.csv"
TICKETS_CSV = DATA_DIR / "it_tickets.csv"


# =============== HELPERS ===============

def load_table(table_name, csv_path):
    """
    Try to load a table from the database.
    If it fails or is empty, load from CSV and save to the database.
    """
    conn = get_db_connection()

    try:
        # Try to read table from the database
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        if df.empty:
            # If table has no rows, we use the CSV
            raise ValueError("table is empty")
    except Exception:
        # If table does not exist or error happens, read from CSV
        df = pd.read_csv(csv_path)
        # Save CSV data into the database table
        df.to_sql(table_name, conn, if_exists="replace", index=False)

    conn.close()
    return df


def run_query(sql, params=()):
    """
    Run a write query (INSERT, UPDATE, DELETE) and then close the connection.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    conn.close()


def update_row(table, id_column, row_id, **kwargs):
    """
    Helper to update one row in any table.
    table: table name as string
    id_column: primary key column name
    row_id: id value to find the row
    kwargs: columns and new values
    """
    # Build part like: "name = ?, rows = ?"
    set_clause = ", ".join([f"{col} = ?" for col in kwargs.keys()])
    values = list(kwargs.values()) + [row_id]

    run_query(
        f"UPDATE {table} SET {set_clause} WHERE {id_column} = ?",
        values
    )


def delete_row(table, id_column, row_id):
    """
    Helper to delete one row in any table.
    """
    run_query(
        f"DELETE FROM {table} WHERE {id_column} = ?",
        (row_id,)
    )


# =============== LOADERS ===============

def load_cyber_incidents():
    """Load cyber_incidents table (or from CSV if needed)."""
    return load_table("cyber_incidents", CYBER_CSV)


def load_datasets_metadata():
    """Load datasets_metadata table (or from CSV if needed)."""
    return load_table("datasets_metadata", DATASETS_CSV)


def load_it_tickets():
    """Load it_tickets table (or from CSV if needed)."""
    return load_table("it_tickets", TICKETS_CSV)


# =============== CYBER INCIDENTS CRUD ===============

def create_incident(incident_id, timestamp, severity, category, status, description):
    """
    Add a new cyber incident row into the table.
    """
    run_query(
        "INSERT INTO cyber_incidents VALUES (?, ?, ?, ?, ?, ?)",
        (incident_id, timestamp, severity, category, status, description)
    )


def update_incident(incident_id, **kwargs):
    """
    Update one cyber incident by its id.
    kwargs can be: status="Closed", severity="Low", etc.
    """
    update_row("cyber_incidents", "incident_id", incident_id, **kwargs)


def delete_incident(incident_id):
    """
    Delete one cyber incident from the table.
    """
    delete_row("cyber_incidents", "incident_id", incident_id)


# =============== DATASETS CRUD ===============

def create_dataset(dataset_id, name, rows, columns, uploaded_by, upload_date):
    """
    Add a new dataset metadata row into the table.
    """
    run_query(
        "INSERT INTO datasets_metadata VALUES (?, ?, ?, ?, ?, ?)",
        (dataset_id, name, rows, columns, uploaded_by, upload_date)
    )


def update_dataset(dataset_id, **kwargs):
    """
    Update one dataset row by its id.
    Example: update_dataset(1, name="New Name", rows=5000)
    """
    update_row("datasets_metadata", "dataset_id", dataset_id, **kwargs)


def delete_dataset(dataset_id):
    """
    Delete one dataset from the table.
    """
    delete_row("datasets_metadata", "dataset_id", dataset_id)


# =============== IT TICKETS CRUD ===============

def create_ticket(ticket_id, priority, description, status, assigned_to, created_at, resolution_time):
    """
    Add a new IT ticket row into the table.
    """
    run_query(
        "INSERT INTO it_tickets VALUES (?, ?, ?, ?, ?, ?, ?)",
        (ticket_id, priority, description, status, assigned_to, created_at, resolution_time)
    )


def update_ticket(ticket_id, **kwargs):
    """
    Update one IT ticket by its id.
    Example: update_ticket(3, status="Resolved", resolution_time_hours=5.5)
    """
    update_row("it_tickets", "ticket_id", ticket_id, **kwargs)


def delete_ticket(ticket_id):
    """
    Delete one IT ticket from the table.
    """
    delete_row("it_tickets", "ticket_id", ticket_id)
