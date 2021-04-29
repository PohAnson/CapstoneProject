"""Contains function to carry out validation."""
import datastore as ds
from datastore import SQLcmds


def validate_stops(*stops_code):
    """Ensure that bus stops is valid

    Returns:
        bool: Whether it is a valid stop
    """
    for stop in stops_code:
        if len(ds.execute(SQLcmds["get_bus_stop_info"], (stop,))) == 0:
            return False
    return True
