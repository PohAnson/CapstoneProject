"""All functionalities to deal with the database."""

import sqlite3

import config
from .sqlcmds import SQLcmds


def get_connection():
    """
    Return a connection to the database in `config.py`.

    Returns:
        sqlite3.Connection: the connection to the sqlite3 database
    """
    return sqlite3.connect(config.db_path)


def execute(cmd, parameters=None):
    """
    To ease the execution of single SQL commands.

    Args:
        cmd (str): Command to be executed
        parameters (iterable, optional): Parameters to be passed to the SQL
        commands. Defaults to None.

    Returns:
        list: list of the results of the SQL commands
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if parameters is None:
        cur.execute(cmd)
    else:
        cur.execute(cmd, parameters)

    results = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return results


def create_table(table_name):
    """
    Create a specified table.

    Args:
        table_name (str):
            Name of table limited to
            {"bus_stops","bus_services", "bus_routes", "fares"}
    """
    execute(SQLcmds[f"create_{table_name}_table"])


def insert_bus_stops(bus_stops):
    """
    Insert bus stops data into the database.

    Args:
        bus_stops (list):
            list of dictionaries with keys \
            (bus_stop_code, road_name, description, latitude, longitude)
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.executemany(SQLcmds["insert_bus_stops"], bus_stops)
    conn.commit()
    cur.close()
    conn.close()


def insert_bus_routes(bus_routes):
    """Insert bus routes data to database.

    Args:
        bus_routes (list):
            list of dictionaries with keys \
            (service_no, direction, stop_sequence, bus_stop_code, distance)
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.executemany(SQLcmds["insert_bus_routes"], bus_routes)
    conn.commit()
    cur.close()
    conn.close()


def retrieve_all(table_name):
    """
    Get all data from a specified table name.

    Args:
        table_name (str): Name of table limited to
        {"bus_stops","bus_services", "bus_routes", "fares"}

    Returns:
        list: list with elements of dictionary
    """
    conn = sqlite3.connect(config.db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        f"""SELECT * FROM {table_name};""",
    )
    result = [dict(row) for row in cur.fetchall()]

    cur.close()
    conn.close()
    return result
