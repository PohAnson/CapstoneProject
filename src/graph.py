"""Graph class"""
import json
import os

import datastore as ds
import bus_utils as bu
from datastore.sqlcmds import SQLcmds
from config import graph_path

###############################################################################
################################# Graph Class #################################
###############################################################################
class Graph:
    """
    Graph of connection between bus stop using their code.

    Attributes:

        - graph (dict): Stored similar to an adjacency list. Each stop is connected to all possible stop that can be reached directly.



    Methods:
        
        - insert(origin_stop_code, end_stop_code): Insert an edge into graph.
        - create_graph([cache]): Create graph, and store it as an attribute
        - serialise(fp): Serialise it as json in a file
        - deserialise(fp): deserialise data from a file
        - search_path(start, end): find a possible path 
    """

    def __init__(self):
        """
        Create an empty graph.

        graph:
            key:BusStopCode,
            value: List of destination reachable from bus stop
        """
        self.graph = {}

    def __repr__(self):
        return self.graph

    def __str__(self):
        return str(self.graph)

    def insert(self, origin_stop_code, end_stop_code):
        """
        Insert an edge into the graph.

        Args:
            origin_bus_stop_code (str): starting bus stop code
            end_bus_stop_code (str): ending bus stop code
        """
        if origin_stop_code not in self.graph:
            self.graph[origin_stop_code] = [end_stop_code]
        else:
            self.graph[origin_stop_code].append(end_stop_code)

    def create_graph(self, cache=True):
        """
        Create and store graph.

        Args:
            cache (bool, optional):
                Whether to use cached result. Recreate graph if unavailable and save it.
                Defaults to True.

        Returns:
            dictionary:
                key: bus_stop_code,
                value: List of destination bus stop code reachable from BusStop
        """
        # Try to read file from cache
        if cache and os.path.isfile(graph_path):
            with open(graph_path, "r") as f:
                self.graph = json.load(f)
            return self.graph
        print('cache unavailable')
        bus_stops = bu.retrieve_all_bus_stops().keys()
        for bus_stop in bus_stops:
            stops = bu.find_bus_connection(bus_stop)
            if len(stops) != 0:
                for stop in stops:
                    self.insert(bus_stop, stop)
            else:
                self.graph[bus_stop] = []
        if cache:
            self.serialise(graph_path)
        return self.graph

    def serialise(self, fp):
        with open(fp, "w") as f:
            json.dump(self.graph, f, indent=2)

    @classmethod
    def deserialise(cls, fp):
        with open(fp, "r") as f:
            self.graph = json.load(f)

    def search_path(self, start, end):
        """Find a possible path.

        Args:
            start (str): Starting bus stop code.
            end (str): Ending bus stop code.

        Returns:
            list: List of all the possible paths
        """
        solution = []
        visited = []
        to_visit = [[start]]

        while to_visit:
            current_path = to_visit.pop(0)
            if len(current_path) > 3 and len(solution) != 0:
                return solution
            if current_path[-1] not in self.graph and current_path[-1] != "CTE":
                for stop in bu.find_bus_connection(current_path[-1]):
                    self.insert(current_path[-1], stop)

            for node in self.graph.get(current_path[-1], []):
                if node not in visited:
                    to_visit.append(current_path + [node])
                    visited.append(node)
                if node == end:
                    solution.append(current_path + [node])

        return solution
