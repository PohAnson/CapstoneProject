import sqlite3

from .sqlcmds import SQLcmds


class Datastore:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self, db_path: str = "src/datastore/database.db") -> None:
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        """
        Return a connection to the database in `config.py`.

        Returns:
            sqlite3.Connection: the connection to the sqlite3 database
        """
        return sqlite3.connect(self.db_path)

    def execute(self, cmd, parameters=None) -> list:
        """
        To ease the execution of single SQL commands.

        Args:
            cmd (str): Command to be executed
            parameters (iterable, optional): Parameters to be passed to the SQL
            commands. Defaults to None.

        Returns:
            list: list of the results of the SQL commands
        """
        conn = self.get_connection()
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

    def create_table(self, table_name: str) -> None:
        """
        Create a specified table.

        Args:
            table_name (str):
                Name of table limited to
                {"bus_stops", "bus_routes"}
        """
        self.execute(SQLcmds[f"create_{table_name}_table"])

    def insert_into_table(self, table_name: str, records: list[dict]):
        """
        Insert record data into the database.

        Args:
            records (list):
                list of dictionaries containing the record
        """
        conn = self.get_connection()
        cur = conn.cursor()
        cur.executemany(SQLcmds[f"insert_{table_name}"], records)
        conn.commit()
        cur.close()
        conn.close()

    def insert_bus_stops(self, bus_stops: list[dict]) -> None:
        """
        Insert bus stops data into the database.

        Args:
            bus_stops (list):
                list of dictionaries with keys \
                (bus_stop_code, road_name, description, latitude, longitude)
        """
        self.insert_into_table('bus_stops', bus_stops)

    def insert_bus_routes(self, bus_routes: list[dict]) -> None:
        """Insert bus routes data to database.

        Args:
            bus_routes (list):
                list of dictionaries with keys \
                (service_no, direction, stop_sequence, bus_stop_code, distance)
        """
        self.insert_into_table('bus_routes', bus_routes)

    def retrieve_all(self, table_name: str) -> list[dict]:
        """
        Get all data from a specified table name.

        Args:
            table_name (str):
                Name of table limited to
                {"bus_stops", "bus_routes"}

        Returns:
            list: list with elements of dictionary
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            f"""SELECT * FROM {table_name};""",
        )
        result = [dict(row) for row in cur.fetchall()]

        cur.close()
        conn.close()
        return result

    def get_bus_stop_info(self, bus_stop_code: str) -> dict:
        """Retrieve info of a bus stop.

        Args:
            bus_stop_code (str): valid bus stop code.

        Raises:
            LookupError: When invalid bus stop code is given

        Returns:
            dict: dictionary with the info of the bus stop.
        """
        bus_stop_info = self.execute(
            SQLcmds["get_bus_stop_info"], (bus_stop_code,))

        if len(bus_stop_info) == 0:
            print(bus_stop_code)
            raise LookupError("Invalid bus stop")

        bus_stop_info = dict(zip(bus_stop_info[0].keys(), bus_stop_info[0]))
        return bus_stop_info

    def get_buses_at(self, bus_stop_code) -> list[sqlite3.Row]:
        return self.execute(
            SQLcmds["get_buses_at"],
            (bus_stop_code, )
        )

    def get_bus_routes(self, service_no: str, direction: int) -> list[str]:
        """Returns list of bus stop code

        Args:
            service_no (str): the service number
            direction (int): the direction it is travelling

        Returns:
            list[str]: list of bus stop code
        """
        return [row[0] for row in self.execute(
            SQLcmds["get_bus_routes"],
            (service_no, direction),
        )]

    def get_distances(self, bus_stop_code, service_no, direction):
        return [
            i[0]
            for i in self.execute(
                SQLcmds["get_distance"],
                (bus_stop_code, service_no, direction),
            )
        ]
