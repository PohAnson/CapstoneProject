from typing import Any, Type

from datastore import Datastore
from datastore import SQLcmds

from . import Bus
ds = Datastore()


class BusStop():
    """BusStop Classes for dealing with bus stop information such as bus_stop_code, road_name, etc."""
    __created_stops: dict[str, "BusStop"] = {}  # stop_code: BusStop

    def __init__(self,
                 bus_stop_code: str,
                 road_name=None,
                 description=None,
                 latitude=None,
                 longitude=None):
        self.bus_stop_code = bus_stop_code
        self.road_name = road_name
        self.description = description
        self.latitude = latitude
        self.longitude = longitude

    def __new__(cls: Type["BusStop"], *args, **kwargs) -> "BusStop":
        if args[0] not in cls.__created_stops.keys():
            cls.__created_stops[args[0]] = object.__new__(cls)
        return cls.__created_stops[args[0]]

    def __repr__(self) -> str:
        return ("BusStop("
                f"{self.bus_stop_code}, "
                f"{self.road_name}, "
                f"{self.description}, "
                f"{self.latitude}, "
                f"{self.longitude}"
                ")"
                )

    def __str__(self) -> str:
        return f"BusStop({self.bus_stop_code})"

    def __getitem__(self, key: str) -> Any:
        attributes = self.to_dict()
        if key not in attributes.keys():
            raise KeyError(f"{key} not a valid field for BusStop")
        return attributes[key]

    @classmethod
    def from_record(cls: Type["BusStop"], **kwargs) -> "BusStop":
        """Create BusStop from record. Should have all the field as kwargs.

        Args:
            cls (BusStop): class

        Returns:
            BusStop: BusStop instance.
        """
        return cls(kwargs.pop('bus_stop_code'), **kwargs)

    @classmethod
    def from_bus_code(cls: Type["BusStop"], bus_stop_code: str) -> "BusStop":
        """Create BusStop with the data when given a bus_stop_code.

        Args:
            cls (BusStop): class
            bus_stop_code (str): valid bus stop code.

        Raises:
            LookupError: When invalid bus stop code is given.

        Returns:
            BusStop: BusStop instance.
        """
        if bus_stop_code in cls.__created_stops.keys():
            return cls.__created_stops[bus_stop_code]
        bus_stop_info = ds.get_bus_stop_info(bus_stop_code)

        return cls(
            bus_stop_code,
            bus_stop_info.get("road_name"),
            bus_stop_info.get("description"),
            latitude=bus_stop_info.get("latitude"),
            longitude=bus_stop_info.get("longitude"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert its field to dictionary.

        Returns:
            dict[str, Any]: field name as dict key and corresponding value.
        """
        return {
            "bus_stop_code": self.bus_stop_code,
            "road_name": self.road_name,
            "description": self.description,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

    def get_buses(self) -> set[Bus]:
        """Get the buses at this bus stop.

        Returns:
            list: list of buses at the bus stop.
        """
        return {Bus(*bus_row)
                for bus_row in ds.get_buses_at(self.bus_stop_code)
                }

    def find_bus_connection(self) -> list["BusStop"]:
        """
        Find the possible all bus_stop reachable from the current bus_stop.

        Returns:
            list: Contains the list of directly connected bus stops.
            Returns empty list if none.
        """
        # avoid continuously opening and closing connection
        conn = ds.get_connection()

        bus_routes = []
        for bus in self.get_buses():
            for stop in conn.execute(
                SQLcmds["find_connected_bus_stop"],
                (bus.service_no, bus.direction, bus.stop_sequence)
            ):
                if stop[0] != 'CTE':
                    bus_routes.extend([BusStop.from_bus_code(stop[0])])
        conn.close()
        return bus_routes

    def buses_to(self, end_stop: "BusStop") -> list["BusRoute"]:
        """
        Find buses from stop to end bus stop.

        Args:
            end_stop (str): ending bus stop

        Returns:
            list: containing BusRoute
        """
        return [
            BusRoute(bus.service_no, bus.direction, self, end_stop)
            for bus in set.intersection(self.get_buses(), end_stop.get_buses())
        ]


class BusRoute:
    """BusRoute class to deal with the route associated to each service.
    """

    def __init__(self,
                 service_no: str,
                 direction: int,
                 start_stop: BusStop = None,
                 end_stop: BusStop = None) -> None:
        self.service_no: str = service_no
        self.direction: int = direction
        self.bus_stops: list[BusStop] = [
            BusStop.from_bus_code(bus_code)
            for bus_code in ds.get_bus_routes(service_no, direction)
        ]
        self.start_stop = start_stop
        self.end_stop = end_stop

    def __repr__(self) -> str:
        return ("\nBusRoute("
                f"{self.service_no}, "
                f"{self.direction}, "
                f"{self.start_stop}, "
                f"{self.end_stop}"
                ")")

    def has_bus_stop(self, bus_stop: BusStop) -> bool:
        """Check if bus stop is along the route.

        Args:
            bus_stop (BusStop): the bus stop to check.

        Returns:
            bool: true if it is along the route.
        """
        return any(
            stop == bus_stop
            for stop in self.bus_stops
        )

    def find_dist(self, bus_stop: BusStop) -> list:
        """
        Find the distance of the service at bus stop measured from start.


        Args:
            bus_stop (BusStop): the bus stop

        Returns:
            list: containing distances ordered by ascending stop sequence
        """
        return ds.get_distances(
            bus_stop.bus_stop_code,
            self.service_no,
            self.direction)

    def calculate_distance(self) -> float:
        """
        Calculate the total distance of a path, using specific bus services.
        Must have end_stop and start_stop set.

        Returns:
            float: the total distance.
        """
        if self.start_stop is None or self.end_stop is None:
            raise ValueError("Start and End stop should not be None")
        return abs(
            self.find_dist(self.end_stop)[-1]
            - self.find_dist(self.start_stop)[0]
        )
