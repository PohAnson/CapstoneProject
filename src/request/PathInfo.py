from typing import Any

from BusClasses import BusStop
from pathfinding import sort_paths
from response import PathInfoSuccess, Result, ResultError
from webui import DetailedPathResult

from .BaseRequest import Request


class PathInfoRequest(Request):
    def handle(self) -> Result:
        path_list = self.flask_request.args.get("path", "").split(" ")
        path_list = [BusStop.from_bus_code(code) for code in path_list]
        dist = self.flask_request.args.get("distance", "")
        paths = sort_paths(
            [path_list], "dist"
        )

        path_len = len(path_list)

        if path_len == 0:
            return ResultError("No valid path given")

        filtered_path = list(filter(lambda path: str(path['dist']) == dist,
                                    paths))
        # None of the path is equal to the dist, put all paths.
        if filtered_path == []:
            filtered_path = paths

        # to add all the services that is available between stops
        services = [set() for _ in range(path_len - 1)]
        path: dict[str, Any]
        for path in filtered_path:
            for i in range(path_len - 1):
                services[i].add((path["sn"][i]))
        detailed_results = [
            DetailedPathResult(services[i], path_list[i])
            for i in range(path_len - 1)
        ]

        # include the ending stop
        detailed_results.append(DetailedPathResult(set(), path_list[-1]))

        response = PathInfoSuccess('/')
        response.set_detailed_path_results(detailed_results)
        response.readable_path = f" {chr(0x1f86a)} ".join(
            [
                stop.description
                for stop in paths[0]["path"]
            ]
        )

        return response
