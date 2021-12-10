"""Graph class"""
from __future__ import annotations

import json
import os

import config
from bus import BusStop, retrieve_all_bus_stops


class Graph:
    """
    Graph of connection between bus stop using their code.

    Attributes:

        - stops_graph (dict): Stored similar to an adjacency list.
            Each stop is connected to all stop that can be reached directly.

    Methods:

        - insert(origin_stop, end_stop): Insert an edge into graph.
        - create_graph([cache]): Create graph, and store it as an attribute
        - json_graph(): return json of the graph
        - serialise(fp): Serialise it as json in a file
        - deserialise(fp): deserialise data from a file
        - search_path(start, end): find a possible path
    """

    def __init__(self, graph: dict[BusStop, list[BusStop]] = None) -> None:
        """
        Create an empty graph.

        graph:
            key:BusStop,
            value: List of destination reachable from bus stop
        """
        self.stops_graph = graph if graph is not None else {}

    def __repr__(self) -> str:
        return str(self.stops_graph)

    def __str__(self) -> str:
        return str(self.stops_graph)

    def insert(self, origin_stop: BusStop, end_stop: BusStop) -> None:
        """
        Insert an edge into the graph.

        Args:
            origin_stop (BusStop): starting bus stop
            end_stop (BusStop): ending bus stop
        """
        if origin_stop not in self.stops_graph:
            self.stops_graph[origin_stop] = [end_stop]
        else:
            self.stops_graph[origin_stop].append(end_stop)

    def create_graph(self, cache: bool = True) -> dict[BusStop, list[BusStop]]:
        """
        Create and store graph.

        Args:
            cache (bool, optional):
                Whether to use cached result. Recreate graph if unavailable
                and save it.
                Defaults to True.

        Returns:
            dictionary:
                key: origin BusStop,
                value: List of destination BusS reachable from BusStop
        """
        # Try to read file from cache
        if cache and os.path.isfile(config.graph_path):
            with open(config.graph_path, "r") as f:
                self.stops_graph = json.load(f)
            return self.stops_graph
        print('cache unavailable')

        # Generating new graph
        bus_stops = retrieve_all_bus_stops()
        for bus_stop in bus_stops.values():
            stops = bus_stop.find_bus_connection()
            if len(stops) != 0:
                for stop in stops:
                    self.insert(bus_stop, stop)
            else:
                self.stops_graph[bus_stop] = []
        return self.stops_graph

    def json_graph(self) -> dict[str, list[str]]:
        """Convert graph to json.

        Returns:
            dict[str, list[str]]: json of the graph.
        """
        return {k.bus_stop_code:
                [val.bus_stop_code for val in vals]
                for k, vals in self.stops_graph.items()}

    def serialise(self, fp: str) -> None:
        """Serialise graph to file.

        Args:
            fp (str): filepath to save graph to.
        """
        with open(fp, "w") as f:
            json.dump(self.json_graph(), f, indent=2)

    @classmethod
    def deserialise(cls, fp: str) -> "Graph":
        """Deserialise a json graph.

        Returns:
            Graph: graph instance
        """
        with open(fp, "r") as f:
            json_graph = json.load(f)
            return cls({BusStop.from_bus_code(k):
                        [BusStop.from_bus_code(val) for val in vals]
                        for k, vals in json_graph.items()})

    def search_path(self, start: BusStop, end: BusStop) -> list[list[BusStop]]:
        """Find a possible path. (Breadth-First)

        Interested in only the connection and not the exact service to take.

        Args:
            start (BusStop): Starting bus stop.
            end (BusStop): Ending bus stop.

        Returns:
            list[list[BusStop]]: Lists of path list
        """
        solutions = []
        visited = set()
        to_visit = [[start]]

        while to_visit:  # still got paths to check.
            current_path = to_visit.pop(0)
            cur_path_last_stop = current_path[-1]

            # terminate search early when there's a solution and
            # current path has more than 3 transfers.
            if solutions and len(current_path) > 3:
                return solutions

            # Check for valid stops in the current path.
            if cur_path_last_stop not in self.stops_graph:
                # Attempt to find connection in case of corrupt data.
                self.reconnecting_stop(cur_path_last_stop)

            # iterating through each connections
            for node in self.stops_graph.get(cur_path_last_stop, []):
                if node not in visited:
                    to_visit.append(current_path + [node])
                    visited.add(node)
                if node == end:
                    solutions.append(current_path + [node])

        return solutions

    def reconnecting_stop(self, origin_stop: BusStop):
        """Find the connections for a stop.

        Args:
            origin_stop (BusStop): The stop to find the connection from.
        """
        for end_stop in origin_stop.find_bus_connection():
            self.insert(origin_stop, end_stop)
