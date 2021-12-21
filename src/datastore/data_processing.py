"""
To help to process data and converting to a usable form.

Running this will help to save all the data in a database.
"""

import json
import os


def read_bus_stops(filepath):
    """Read the bus stop from json file.

    Args:
        filepath (str): Filepath of the bus stop json file

    Returns:
        list of dict: keys : ("bus_stop_code", "road_name", "description",
        "latitude", "longitude")
    """
    datas = []
    with open(filepath, "r", newline="") as f:
        bus_stops_data = json.load(f)
        for bus_stop in bus_stops_data:
            tmp = {
                'bus_stop_code': bus_stop["BusStopCode"],
                'road_name': bus_stop["RoadName"],
                'description': bus_stop["Description"],
                'latitude': bus_stop["Latitude"],
                'longitude': bus_stop["Longitude"],
            }

            datas.append(tmp)
    return datas


def read_bus_routes(filepath):
    """Read the bus routes data from json path.

    Args:
        filepath (str): file path of bus routes json.

    Returns:
        list:
            list of dictionary with keys
            (service_no, direction, stop_sequence, bus_stop_code, distance)
    """
    datas = []
    with open(filepath, "r") as f:
        bus_routes = json.load(f)
        for bus_route in bus_routes:
            tmp =s {
                'service_no': bus_route["ServiceNo"],
                'direction': bus_route["Direction"],
                'stop_sequence': bus_route["StopSequence"],
                'bus_stop_code': bus_route["BusStopCode"],
                'distance': bus_route["Distance"],
            }

            datas.append(tmp)
    return datas


if __name__ == "__main__":
    # so the config files can be found
    import sys
    sys.path.append(os.getcwd()+'/src')

    import config

    from datastore import Datastore

    ds = Datastore(config.db_path)
    ds.execute('DROP TABLE IF EXISTS "bus_stops";')
    ds.execute('DROP TABLE IF EXISTS "bus_routes"')

    ds.create_table('bus_stops')
    ds.create_table('bus_routes')

    bus_stops = read_bus_stops(os.path.sep.join(
        ["src", "data", "bus_stops.json"]))
    bus_routes = read_bus_routes(
        os.path.sep.join(["src", "data", "bus_routes.json"]))
    ds.insert_bus_stops(bus_stops)
    ds.insert_bus_routes(bus_routes)
