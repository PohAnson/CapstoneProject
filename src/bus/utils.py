"""Utilities function to deal with bus."""

import datastore as ds

from . import BusRoute, BusStop


def find_bus_path(path: list[BusStop]) -> list[list["BusRoute"]]:
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


def retrieve_all_bus_stops() -> dict[str, "BusStop"]:
    """
    Get all bus stop datas from the database.

    Returns:
        dictionary: {bus_stop_code (str): BusStop}
    """
    return {
        data["bus_stop_code"]: BusStop.from_record(**data)
        for data in ds.retrieve_all("bus_stops")
    }
