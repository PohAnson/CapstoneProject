"""This modules contains request that process the request and
should returned a Result object"""

from typing import Any

import bus_utils as bu
import response as res
from pathfinding import sort_paths
from validation import validate_stops
from webui import DetailedPathResult, PathsResult


class Request:
    def __init__(self, flask_request):
        self.flask_request = flask_request

    def handle(self) -> res.Result:
        raise NotImplementedError


class PathSummaryRequest(Request):
    def to_find_path(self) -> list:
        return [self.start_stop_code, self.end_stop_code, self.criteria]

    def validate(self) -> res.Result:
        """Validate the input given and give a status page

        Returns:
            res.Result: The result of the validation.
                        If invalid, show error page.
                        Else show the processing page.
        """
        start_stop_code = self.flask_request.form.get("start_stop_code", None)
        end_stop_code = self.flask_request.form.get("end_stop_code", None)
        criteria = self.flask_request.form.get("criteria", None)

        # Validating info
        if None in (start_stop_code, end_stop_code, criteria):
            return res.ResultError(message="There is no input for starting or \
                                    ending stop code")
        elif not validate_stops(start_stop_code, end_stop_code):
            return res.ResultError(message="Invalid bus stop code is given")

        # setting variable
        self.start_stop_code = start_stop_code
        self.end_stop_code = end_stop_code
        self.criteria = criteria
        return res.ProcessingSuccess()

    def handle(self) -> res.Result:
        return res.PathSummarySuccess(self.results)

    def set_paths_summary(self, datas: list[dict[str, Any]],
                          summarise: bool = True) -> list[PathsResult]:
        """Set the result table.

        Args:
            datas (list): contain dictionary with key(sn, path, dist, transfer)
            summarise (bool, optional): Whether to summarise data. Defaults to True.
        """
        if summarise:

            def summarise_data(datas: list[dict[str, Any]]) -> list[dict[str, Any]]:
                """Summarise datas. Remove duplicate of same distance & service
                number AND same distance and path taken.

                Args:
                    datas (list): contain dictionary with key(sn, path, dist,
                    transfer)

                Returns:
                    list: contain dictionary with key(sn, path, dist, transfer)
                """
                partial_summary = {}
                summary = {}
                data: dict[str, Any]
                for data in datas:
                    partial_summary[(tuple(data["sn"]),
                                     str(["dist"]))] = data
                item: dict[str, Any]
                for item in partial_summary.values():
                    summary[(str(item["dist"]), tuple(item["path"]))] = item
                summary: dict[tuple, dict[str, Any]]
                return list(summary.values())

            datas = summarise_data(datas)

        self.results = [
            PathsResult(data["sn"], data["path"], data["dist"])
            for data in datas
        ]
        return self.results


class PathInfoRequest(Request):
    def handle(self) -> res.Result:
        path_list = self.flask_request.args.get("path", "").split(" ")
        dist = self.flask_request.args.get("distance", "")

        paths = sort_paths([path_list], "dist")
        path_len = len(path_list)

        if path_len == 0:
            return res.ResultError("No valid path given")

        filtered_path = list(filter(lambda path: str(path['dist']) == dist,
                                    paths.data))
        # None of the path is equal to the dist, put all paths.
        if filtered_path == []:
            filtered_path = paths

        # to add all the services that is available between stops
        services = [set() for _ in range(path_len - 1)]
        for path in filtered_path:
            for i in range(path_len - 1):
                services[i].add((path["sn"][i]))
        detailed_results = [
            DetailedPathResult(services[i], path_list[i])
            for i in range(path_len - 1)
        ]

        # include the ending stop
        detailed_results.append(DetailedPathResult(set(), path_list[-1]))

        response = res.PathInfoSuccess('/')
        response.set_detailed_path_results(detailed_results)
        response.readable_path = f" {chr(0x1f86a)} ".join(
            [
                bu.get_bus_stop_info(stop_code)["description"]
                for stop_code in paths[0]["path"]
            ]
        )

        return response
