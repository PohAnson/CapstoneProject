"""To create a WebInterface."""
from flask import jsonify

import bus_utils as bu
import datastore as ds
from datastore import SQLcmds

###############################################################################
############################# ProcessStatus Class #############################
###############################################################################


class ProcessStatus:
    def __init__(self) -> None:
        self.status_done = False
        self.main_status = ""
        self.sub_status = ""

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

    def jsonify(self):
        return jsonify({"status_done": self.status_done,
                        "main_status": self.main_status,
                        "sub_status": self.sub_status, })


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
