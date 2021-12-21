from bus import BusStop


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
        + get_road_description_readable(): Convert the road description to a
         readable format
        + get_road_name_readable(): Convert the road name to a readable format.
    """

    def __init__(self, services, bus_stop: BusStop):
        self.services = sorted(list(services))
        self.bus_stop = bus_stop

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
            return "Buses: " + ", ".join(
                [service for service in self.services]
            )
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
        return self.bus_stop.description

    def get_road_name_readable(self):
        """Convert road name to a readable format.

        Returns:
            str: Road name
        """
        return self.bus_stop.road_name
