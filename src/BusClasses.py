"""Functions to deal with bus stops and routes."""

from typing import Any, Generic, Type, TypeVar

import datastore as ds
from datastore.sqlcmds import SQLcmds


class Bus:
    __created_buses = {}  # (service_no, direction, stop_sequence): Bus

    def __init__(self,
                 service_no: str,
                 direction: int,
                 stop_sequence: int) -> None:
        self.service_no: str = service_no
        self.direction: int = direction
        self.stop_sequence: int = stop_sequence

    def __new__(cls, *args):
        if args not in cls.__created_buses.keys():
            cls.__created_buses[args] = object.__new__(cls)
        return cls.__created_buses[args]

    def __repr__(self) -> str:
        return ("Bus("
                f"{self.service_no}, "
                f"{self.direction}, "
                f"{self.stop_sequence}, "
                f"{self.__hash__()}"
                ")"
                )

    def __hash__(self) -> int:
        return hash(self.service_no) // hash(self.direction)

    def __eq__(self, __o: "Bus") -> bool:
        # Same bus if the service no and direction is same.
        return (self.service_no == __o.service_no
                and self.direction == __o.direction)

    # gt, lt compares the stop sequence
    def __gt__(self, __o):
        return self.stop_sequence > __o.stop_sequence

    def __lt__(self, __o):
        return self.stop_sequence < __o.stop_sequence


_T = TypeVar("_T", bound="BusStop")


class BusStop(Generic[_T]):
    __created_stops: dict[str, _T] = {}  # stop_code: BusStop

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

    def __new__(cls: Type[_T], *args, **kwargs) -> _T:
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
    def from_record(cls: Type[_T], **kwargs) -> _T:
        """Create BusStop from record. Should have all the field as kwargs.

        Args:
            cls (BusStop): class

        Returns:
            BusStop: BusStop instance.
        """
        return cls(kwargs.pop('bus_stop_code'), **kwargs)

    @classmethod
    def from_bus_code(cls: Type[_T], bus_stop_code: str) -> _T:
        """Create BusStop with the data when given a bus_stop_code.

        Args:
            cls (BusStop): class
            bus_stop_code (str): valid bus stop code.

        Raises:
            LookupError: When invalid bus stop code is given

        Returns:
            BusStop: BusStop instance.
        """
        if bus_stop_code in cls.__created_stops.keys():
            return cls.__created_stops[bus_stop_code]
        bus_stop_info = ds.execute(
            SQLcmds["get_bus_stop_info"], (bus_stop_code,))

        if len(bus_stop_info) == 0:
            print(bus_stop_code)
            raise LookupError("Invalid bus stop")

        bus_stop_info = dict(zip(bus_stop_info[0].keys(), bus_stop_info[0]))
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
                for bus_row in ds.execute(
            SQLcmds["get_buses_at"], (self.bus_stop_code,)
        )
        }

    def find_bus_connection(self) -> list["BusStop"]:
        """
        Find the possible all bus_stop reachable from the current bus_stop.

        Returns:
            list: Contains the list of directly connected bus stops.
        """

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
    def __init__(self,
                 service_no: str,
                 direction: int,
                 start_stop: BusStop = None,
                 end_stop: BusStop = None) -> None:
        self.service_no: str = service_no
        self.direction: int = direction
        self.bus_stops: list[BusStop] = [BusStop.from_bus_code(bus_code[0])
                                         for bus_code in ds.execute(
            SQLcmds["get_bus_routes"],
            (service_no, direction),
        )
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
        return [
            i[0]
            for i in ds.execute(
                SQLcmds["get_distance"],
                (bus_stop.bus_stop_code, self.service_no, self.direction),
            )
        ]

    def calculate_distance(self) -> float:
        """
        Calculate the total distance of a path, using specific bus services.

        Returns:
            float: the total distance.
        """
        if self.start_stop is None or self.end_stop is None:
            raise ValueError("Start and End stop should not be None")
        return abs(
            self.find_dist(self.end_stop)[-1]
            - self.find_dist(self.start_stop)[0]
        )


def retrieve_all_bus_stops() -> dict[str, BusStop]:
    """
    Get all bus stop datas from the database.

    Returns:
        dictionary: {bus_stop_code (str): BusStop}
    """
    return {
        data["bus_stop_code"]: BusStop.from_record(**data)
        for data in ds.retrieve_all("bus_stops")
    }


def find_bus_path(path: list[BusStop]) -> list[list[BusRoute]]:
    """
    Find buses connecting a path.

    Args:
        path (list): list of paths

    Returns:
        list of list: list contains all possible paths
    """
    buses_list = [[]]
    for i in range(1, len(path)):
        buses_list.append([])
        for bus in path[i-1].buses_to(path[i]):
            if i == 1:
                buses_list[i].append([bus])
            else:
                for buses in buses_list[i - 1]:
                    buses_list[i].append(buses + [bus])
    return buses_list[-1]  # the last list in buses_list is the full bus route
