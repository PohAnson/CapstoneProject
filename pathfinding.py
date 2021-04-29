"""Functions to help find the path."""

# import datastore as ds
from sort import OrderedList
import bus_utils as bu


def sort_paths(paths, criteria, ui=None):
    """List of paths to find a bus routes and sort.

    Args:
        paths (list): All possible paths to find
        criteria (str): Criteria to sort by in {"dist", "transfer"}
        ui (WebInterface, optional): WebInterface object to update.

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
    if ui is not None:
        ui.clear_status()
        ui.set_status("Finding bus connections", main_status=True)

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
        if ui is not None:
            ui.set_status(f"Found {i+1}/{len(paths)} bus paths")
    if ui is not None:
        ui.clear_status()
        ui.set_status("Finished finding bus connections.", main_status=True)
    return results


def search_path(start_stop_code, end_stop_code, graph, ui=None):
    """Search for all paths between 2 points combination.

    Args:
        combinations (list):
            Contains tuple(start_bus_stop_code, end_bus_stop_code)
        graph (Graph): Graph object with a graph
        ui (WebInterface, optional): The WebInterface object to update.

    Returns:
        list: All the possible paths
    """
    if ui is not None:
        start_info = bu.get_bus_stop_info(start_stop_code)["description"]
        end_info = bu.get_bus_stop_info(end_stop_code)["description"]
        ui.set_status(
            f"Searching for path \
                {start_info} {chr(0x1f86a)} {end_info}",
            main_status=True,
        )
    path_lists = graph.search_path(start_stop_code, end_stop_code)
    return path_lists
