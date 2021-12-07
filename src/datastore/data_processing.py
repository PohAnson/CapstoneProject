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
            tmp = {}
            tmp["bus_stop_code"] = bus_stop["BusStopCode"]
            tmp["road_name"] = bus_stop["RoadName"]
            tmp["description"] = bus_stop["Description"]
            tmp["latitude"] = bus_stop["Latitude"]
            tmp["longitude"] = bus_stop["Longitude"]
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
            tmp = {}
            tmp["service_no"] = bus_route["ServiceNo"]
            tmp["direction"] = bus_route["Direction"]
            tmp["stop_sequence"] = bus_route["StopSequence"]
            tmp["bus_stop_code"] = bus_route["BusStopCode"]
            tmp["distance"] = bus_route["Distance"]
            datas.append(tmp)
    return datas


if __name__ == "__main__":
    import datastore as ds
    from datastore.sqlcmds import SQLcmds
    ds.execute('Drop table "bus_stops";')
    ds.execute('drop table "bus_routes"')

    ds.execute(SQLcmds["create_bus_stops_table"])
    ds.execute(SQLcmds["create_bus_routes_table"])

    bus_stops = read_bus_stops(os.path.sep.join(["datas", "bus_stops.json"]))
    bus_routes = read_bus_routes(
        os.path.sep.join(["datas", "bus_routes.json"]))
    ds.insert_bus_stops(bus_stops)
    ds.insert_bus_routes(bus_routes)
