"""To create a WebInterface."""
from flask import jsonify
import datastore as ds
import bus_utils as bu
from datastore import SQLcmds

###############################################################################
############################# WebInterface Class ##############################
###############################################################################


class WebInterface:
    """To help with storing and giving formatted data.

    Attributes:

        + error_message (str): 
        + main_status (str): 
        + sub_status (str): 
        + results (list): 
        + detailed_results (list): 
        + status_done (bool): 

    Methods:

        + get_status(main_status): Return the status message.
        + set_status(status, [main_status]): Update the status.
        + clear_status(): Clear all status message.
        + get_error_message(): Returns the error message.
        + set_error_message(error): Update the error message. 
        + clear_error_message(): Clear all error message.
        + get_result_table(): Return the results.
        + set_result_table(datas, [summarise]): Set the results table.
        + get_detailed_path_results(): Get results for the details of a path.
        + set_detailed_path_results(paths): Set results for the path's details.
        + clear_detailed_path_results(): Clear all results for path details.
        + jsonify(): Return the json response of relevant datas.
    """

    def __init__(self):
        self.error_message = ""
        self.main_status = ""
        self.sub_status = ""
        self.results = []
        self.detailed_results = []
        self.status_done = False

    def __repr__(self):
        return f"WebInterface(error_message={self.error_message}, main_status={self.main_status}, sub_status={self.sub_status}, results={self.results}, detailed_results={self.detailed_results}, status_done={self.status_done})"

    def get_status(self, main_status):
        """Return status.

        Args:
            status (str): The status message to update
            main_message (bool): Whether to return main message or sub message

        Returns:
            str: Formatted status
        """
        return self.main_status if main_status else self.sub_status

    def set_status(self, status, main_status=False):
        """Update the status.

        Args:
            status (str): The status message to update
            main_status (bool, optional): Whether it is the main status. Defaults to False.
        """
        if not main_status:
            self.sub_status = status
        else:
            self.main_status = status

    def clear_status(self):
        """Clear all the status message."""
        self.main_status = ""
        self.sub_status = ""

    def get_error_message(self):
        """Return the error message.

        Returns:
            str: Error message
        """
        return self.error_message

    def set_error_message(self, error):
        """Update the error message.

        Args:
            error (str): Error message to update to
        """
        self.error_message = error

    def clear_error_message(self):
        """Clear the error message stored."""
        self.error_message = ""

    def get_result_table(self):
        """Return the results.

        Returns:
            list: contains PathsResult object
        """
        return self.results

    def set_result_table(self, datas, summarise=True):
        """Set the result table.

        Args:
            datas (list): contain dictionary with key(sn, path, dist, transfer)
            summarise (bool, optional): Whether to summarise data. Defaults to True.
        """
        if summarise:

            def summarise_results(results):
                """Summarise results.

                Args:
                    results (list): contain dictionary with key(sn, path, dist, transfer)

                Returns:
                    list: contain dictionary with key(sn, path, dist, transfer)
                """
                partial_summary = {}
                summary = {}
                for result in results:
                    partial_summary[(tuple(result["sn"]),
                                     str(["dist"]))] = result
                for item in partial_summary.values():
                    summary[(str(item["dist"]), tuple(item["path"]))] = item
                return summary.values()

            datas = summarise_results(datas)

        self.results = [
            PathsResult(data["sn"], data["path"], data["dist"]) for data in datas
        ]
        self.status_done = True

    def get_detailed_path_results(self):
        """Get the results for the details of a path.

        Returns:
            list: contains DetailedPathResult object
        """
        return self.detailed_results

    def set_detailed_path_results(self, paths):
        """Set the results for the details of a path.

        Args:
            paths (list): contain dictionary with key(sn, path, dist, transfer)
        """
        if len(paths) == 0:
            self.detailed_results = []
            return
        path_len = len(paths[0]["path"])
        path_list = [paths[0]["path"][i] for i in range(path_len)]
        services = []
        for i in range(path_len - 1):
            services.append(set())

        # to add all the services that is availble between stops
        for path in paths:
            for i in range(path_len - 1):
                services[i].add((path["sn"][i]))

        for i in range(path_len - 1):
            self.detailed_results.append(
                DetailedPathResult(services[i], path_list[i]))
        # include the ending stop
        self.detailed_results.append(DetailedPathResult([], path_list[-1]))

    def clear_detailed_path_results(self):
        """Clear all the detailed results."""
        self.detailed_results = []

    def jsonify(self):
        """Return json response of relevant datas.

        Returns:
            Json: Contains key(error_message, status, status_done)
        """
        return jsonify(
            {
                "error_message": self.get_error_message(),
                "main_status": self.get_status(True),
                "sub_status": self.get_status(False),
                "status_done": self.status_done,
            }
        )

###############################################################################
############################## PathsResult Class ##############################
###############################################################################


class PathsResult:
    """
    To help with storing and formatting individual results.

    Attributes:

        + services (list): Contain the tuple (service_no, direction)
        + path (list): The bus stops path
        + distance (float): Total distance of the path

    Methods:

        + get_path_url(): Convert path to unique url
        + get_path_readable(): Convert path to readable format.
        + get_service_readable(): Convert service to a readable format.
        + get_distance_readable(): Convert distance to a readable format.
    """

    def __init__(self, services, path, distance):
        self.services = services
        self.path = path
        self.distance = distance

    def __repr__(self):
        return f"PathsResult({self.services}, {self.path}, {self.distance})"

    def get_path_url(self):
        """Convert path to a unique url path.

        Returns:
            str: link to view the detailed path
        """
        return f"path_info?path={'+'.join(self.path)}&distance={self.distance}"

    def get_path_readable(self):
        """Convert path to a readable format.

        Returns:
            str: path of bus stops as a readable form
        """

        return f" {chr(0x1f86a)} ".join(
            [bu.get_bus_stop_info(path)["description"] for path in self.path]
        )

    def get_service_readable(self):
        """Convert service to a readable format.

        Returns:
            str: service numbers to take as a readable form
        """
        return f" {chr(0x1f86a)} ".join([service[0] for service in self.services])

    def get_distance_readable(self):
        """Convert the distance to a readable format.

        Returns:
            str: distance
        """
        return str(self.distance)

###############################################################################
########################### DetailedPathResult Class ##########################
###############################################################################


class DetailedPathResult:
    """To help with the storing of individual detailed results.

    Attributes:

        + services (list): service number
        + bus_stop (str): bus stop code
        + road_name (str): road name of the stop
        + road_description (str): description of the stop

    Methods:

        + get_service_readable(): Convert the bus service to a readable format.
        + get_bus_stop_readable(): Convert the bus stop to a readable format.
        + get_road_description_readable(): Convert the road description to a readable format
        + get_road_name_readable(): Convert the road name to a readable format.
    """

    def __init__(self, services, bus_stop):
        self.services = sorted(list(services))
        self.bus_stop = bus_stop
        bus_info = ds.execute(SQLcmds["get_bus_stop_info"], (bus_stop,))[0]
        self.road_name, self.road_description = (
            bus_info["road_name"],
            bus_info["description"],
        )

    def __repr__(self):
        """
        Representation of DetailedPathResult object.

        Returns:
            str: Representation of DetailedPathResult object.

        """
        return f"DetailedPathResult({self.services}, {self.bus_stop})"

    def get_service_readable(self):
        """Convert the bus service to a readable format.

        Returns:
            str: Buses that can be taken
        """
        if self.services != []:
            return "Buses: " + ", ".join([i[0] for i in self.services])
        return ""

    def get_bus_stop_readable(self):
        """Convert the bus stop to a readable format.

        Returns:
            str: Bus stop code
        """
        return self.bus_stop

    def get_road_description_readable(self):
        """Convert road description to a readable format.

        Returns:
            str: Road description
        """
        return self.road_description

    def get_road_name_readable(self):
        """Convert road name to a readable format.

        Returns:
            str: Road name
        """
        return self.road_name
