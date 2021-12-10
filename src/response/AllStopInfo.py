from bus import retrieve_all_bus_stops
from flask import jsonify

from .BaseResults import Result


class AllStopInfoResult(Result):
    def __init__(self):
        return

    def html(self):
        return

    def jsonify(self):
        # get the list of bus stop info to show after the user type a code
        all_bus_stop_info = [bus_stop.to_dict()
                             for bus_stop in retrieve_all_bus_stops().values()
                             ]
        for i in range(len(all_bus_stop_info)):
            # need to have a id field to be indexed.
            all_bus_stop_info[i]["id"] = i

        return jsonify(all_bus_stop_info)
