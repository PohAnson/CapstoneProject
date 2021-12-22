from collections import OrderedDict
from typing import Any

from bus import BusStop
from response import PathSummarySuccess, ProcessingSuccess, Result, ResultError
from validation import validate_stops
from webui import PathsResult

from .BaseRequest import Request


class PathSummaryRequest(Request):
    def to_find_path(self) -> list:
        return [self.start_stop, self.end_stop, self.criteria]

    def validate(self) -> Result:
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
            return ResultError(message="There is no input for starting or \
                                    ending stop code")
        elif not validate_stops(start_stop_code, end_stop_code):
            return ResultError(message="Invalid bus stop code is given")

        # setting variable
        self.start_stop = BusStop.from_bus_code(start_stop_code)
        self.end_stop = BusStop.from_bus_code(end_stop_code)
        self.criteria = criteria
        return ProcessingSuccess()

    def handle(self) -> Result:
        return PathSummarySuccess(self.results)

    def set_paths_summary(self, datas: list[dict[str, Any]],
                          summarise: bool = True) -> list[PathsResult]:
        """Set the result table.

        Args:
            datas (list): contain dictionary with key(sn, path, dist, transfer)
            summarise (bool, optional): Whether to summarise data.
                    Defaults to True.
        """
        if summarise:

            datas = self.summarise_data(datas)
        self.results = [
            PathsResult(data["sn"], data["path"], data["dist"])
            for data in datas
        ]
        return self.results

    @staticmethod
    def summarise_data(
        datas: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Summarise datas. Remove duplicate of same distance & service
        number AND same distance and path taken.

        Args:
            datas (list): contain dictionary with key(sn, path, dist,
            transfer)

        Returns:
            list: contain dictionary with key(sn, path, dist, transfer)
        """
        sn_dist_summary = OrderedDict()
        data: dict[str, Any]
        for data in datas:
            if (tuple(data["sn"]),
                    str(["dist"])) not in sn_dist_summary.keys():
                sn_dist_summary[(tuple(data["sn"]),
                                 str(["dist"]))] = data
        summary = OrderedDict()
        item: dict[str, Any]
        for item in sn_dist_summary.values():
            if (str(item["dist"]), tuple(item["path"])) not in summary.keys():
                summary[(str(item["dist"]), tuple(item["path"]))] = item
        return list(summary.values())
