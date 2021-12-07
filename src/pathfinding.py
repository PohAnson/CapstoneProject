"""Functions to help find the path."""

from typing import Any, Optional

from BusClasses import BusStop, find_bus_path
from OrderedList import OrderedList
from Graph import Graph
from webui import ProcessStatus


def search_path(start_stop: BusStop,
                end_stop: BusStop,
                graph: Graph,
                process_status: Optional[ProcessStatus] = None
                ) -> list[list[BusStop]]:
    """Search for all paths between 2 points combination.

    Args:
        combinations (list):
            Contains tuple(start_bus_stop_code, end_bus_stop_code)
        graph (Graph): Graph object with a graph
        process_status (ProcessStatus, optional): The process_status to update.

    Returns:
        list: All the possible paths
    """
    if process_status is not None:
        process_status.set_status(
            f"Searching for path \
            {start_stop.description} {chr(0x1f86a)} {end_stop.description}",
            main_status=True,
        )
    return graph.search_path(start_stop, end_stop)


def sort_paths(paths: list[list[BusStop]],
               criteria: str,
               process_status: Optional[ProcessStatus] = None
               ) -> OrderedList[str, Any]:
    """List of paths to find a bus routes and sort.

    Args:
        paths (list[list[BusStop]]): All possible paths to find
        criteria (str): Criteria to sort by in {"dist", "transfer"}
        process_status (ProcessStatus, optional): process_status to update.

    Raises:
        KeyError: The criteria is not valid

    Returns:
        OrderedList[str, Any]:
            list containing dictionary with key(sn, path, dist, transfer),
            sorted according to the criteria
    """
    if criteria not in {"dist", "transfer"}:
        raise KeyError("Invalid Criteria")
    results = OrderedList(index=criteria)

    if process_status is not None:
        process_status.clear_status()
        process_status.set_status("Finding bus connections", main_status=True)

    # getting results
    for i, path in enumerate(paths):
        for bus_routes in find_bus_path(path):
            total_dist = sum(route.calculate_distance()
                             for route in bus_routes)
            results.insert(
                {
                    "sn": [route.service_no for route in bus_routes],
                    "path": path,
                    "dist": round(total_dist, 2),
                    "transfer": len(bus_routes),
                }
            )

        if process_status is not None:
            process_status.set_status(f"Found {i+1}/{len(paths)} bus paths")

    if process_status is not None:
        process_status.clear_status()
        process_status.set_status(
            "Finished finding bus connections.", main_status=True)
    return results
