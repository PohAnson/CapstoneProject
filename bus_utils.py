"""Functions to deal with bus stops and routes."""
from sort import OrderedList
import datastore as ds
from datastore.sqlcmds import SQLcmds


def get_bus_stop_info(bus_stop_code):
    """Get all the information on a bus stop

    Args:
        bus_stop_code (str): bus stop code

    Returns:
        dict: bus stop information
    """
    bus_stop_info = ds.execute(SQLcmds["get_bus_stop_info"], (bus_stop_code,))[0]
    bus_stop_info = dict(zip(bus_stop_info.keys(), bus_stop_info))

    return bus_stop_info


def get_buses_at(bus_stop_code):
    """
    Find buses at the bus stop by bus_stop_code.

    Args:
        bus_stop_code (str): starting bus stop code

    Returns:
        list: each element is sqlite3.Row with key (service_no, direction, stop_sequence)
    """
    return ds.execute(SQLcmds["get_buses_at"], (bus_stop_code,))


def retrieve_all_bus_stops():
    """
    Get all bus stop datas from the database.

    Returns:
        dictonary: {bus_stop_code (str): bus stop info}
    """
    datas = {}
    for data in ds.retrieve_all("bus_stops"):
        datas[data["bus_stop_code"]] = data
    return datas


def find_bus_path(path):
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
        for bus in bus_between(path[i - 1], path[i]):
            if i == 1:
                buses_list[i].append([bus])
            else:
                for buses in buses_list[i - 1]:
                    buses_list[i].append(buses + [bus])

    return buses_list[-1]  # the last list in buses_list is the full bus path


def find_dist(bus_stop_code, service_no, direction):
    """
    Find the numeric distance of the service at bus stop measured from origin.

    Args:
        bus_stop_code (str): bus stop code of the bus stop to find
        service_no (str): bus number
        direction (int): the direction of the bus

    Returns:
        list: containing distances ordered by ascending stop sequence
    """
    return [
        i[0]
        for i in ds.execute(
            SQLcmds["get_distance"],
            (bus_stop_code, service_no, direction),
        )
    ]


def calculate_distance(paths, service_nos):
    """
    Calculate the total distance of a path, using specific bus services.

    Args:
        paths (list): list of bus stop code string
        service_nos (list): list of service number string

    Returns:
        float: the total distance to nearest 1 dp.
    """
    total_distance = 0
    for i in range(len(paths) - 1):  # -1 for the nubmer of interval
        start_bus_stop_code = paths[i]
        end_bus_stop_code = paths[i + 1]
        service_no, direction = service_nos[i]
        total_distance += abs(
            find_dist(end_bus_stop_code, service_no, direction)[-1]
            - find_dist(start_bus_stop_code, service_no, direction)[0]
        )

    return round(total_distance, 1)


def bus_between(start_code, end_code):
    """
    Find buses between bus stop.

    Args:
        start_code (str): starting bus stop code
        end_code (str): ending bus stop code

    Returns:
        list: containing tuple(service_no, direction)
    """
    results = []
    starting_buses = get_buses_at(start_code)
    ending_buses = get_buses_at(end_code)
    for starting_bus in starting_buses:
        for ending_bus in ending_buses:
            # ensurethe start and end stop have same service_no and direction
            # AND stop sequence of start is lower than end
            if starting_bus[:2] == ending_bus[:2] and starting_bus[2] < ending_bus[2]:
                results.append(ending_bus[:2])
    return results


def find_bus_connection(bus_stop_code):
    """
    Find the possible bus roads from the bus_stop_code.

    Args:
        bus_stop_code (str): bus_stop_code to find all connections from.

    Returns:
        list: Contains the list of directly connected bus stops.
    """

    conn = ds.get_connection()
    buses_data = get_buses_at(bus_stop_code)

    bus_routes = []
    for bus in buses_data:
        bus_routes.extend(
            [i[0] for i in conn.execute(SQLcmds["find_bus_stop_connectivity"], bus)]
        )
    conn.close()
    return bus_routes
