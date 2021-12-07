"""Contains function to carry out validation."""
from BusClasses import BusStop


def validate_stops(*stops_code: str):
    """Ensure that bus stops is valid

    Returns:
        bool: Whether it is a valid stop
    """
    for stop in stops_code:
        try:
            BusStop.from_bus_code(stop)
        except LookupError:
            return False
    return True
