"""Functions to help find the path."""

import bus_utils as bu
from graph import Graph
from sort import OrderedList


def sort_paths(paths, criteria, process_status=None):
    """List of paths to find a bus routes and sort.

    Args:
        paths (list): All possible paths to find
        criteria (str): Criteria to sort by in {"dist", "transfer"}
        process_status (ProcessStatus, optional): process_status to update.

    Raises:
        KeyError: The criteria is not valid

    Returns:
        OrderedList:
            list containing dictionary with key(sn, path, dist, transfer),
            sorted according to the criteria
    """
    if criteria not in {"dist", "transfer"}:
        raise KeyError("Invalid Criteria")
    results = OrderedList(index=criteria)
    if process_status is not None:
        process_status.clear_status()
        process_status.set_status("Finding bus connections", main_status=True)

    for i, path in enumerate(paths):
        service_nos = bu.find_bus_path(path)
        for service_no in service_nos:
            dist = bu.calculate_distance(path, service_no)
            results.insert(
                {
                    "sn": service_no,
                    "path": path,
                    "dist": dist,
                    "transfer": len(service_no),
                }
            )
        if process_status is not None:
            process_status.set_status(f"Found {i+1}/{len(paths)} bus paths")
    if process_status is not None:
        process_status.clear_status()
        process_status.set_status(
            "Finished finding bus connections.", main_status=True)
    return results


def search_path(start_stop_code, end_stop_code, graph, process_status=None):
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
        start_info = bu.get_bus_stop_info(start_stop_code)["description"]
        end_info = bu.get_bus_stop_info(end_stop_code)["description"]
        process_status.set_status(
            f"Searching for path \
                {start_info} {chr(0x1f86a)} {end_info}",
            main_status=True,
        )
    return graph.search_path(start_stop_code, end_stop_code)
