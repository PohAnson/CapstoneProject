from BusClasses import BusStop


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

    def __init__(self, services: list, path: list[BusStop], distance):
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
        joined_path = '+'.join([stop.bus_stop_code for stop in self.path])
        return f"path_info?path={joined_path}&distance={self.distance}"

    def get_path_readable(self):
        """Convert path to a readable format.

        Returns:
            str: path of bus stops as a readable form
        """

        return f" {chr(0x1f86a)} ".join(
            [stop.description for stop in self.path]
        )

    def get_service_readable(self):
        """Convert service to a readable format.

        Returns:
            str: service numbers to take as a readable form
        """
        return f" {chr(0x1f86a)} ".join([service for service in self.services])

    def get_distance_readable(self):
        """Convert the distance to a readable format.

        Returns:
            str: distance
        """
        return str(self.distance)
