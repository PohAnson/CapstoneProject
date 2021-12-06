"""File to start the flask app."""
from threading import Thread

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

import bus_utils as bu
import request as req
from config import host, port
from graph import Graph
from pathfinding import search_path, sort_paths
from webui import ProcessStatus

app = Flask(__name__)
app.secret_key = "098765456789"
CORS(app)


@app.route("/")
def root():
    """Return page containing the form."""
    return render_template("index.html")


@app.route("/processing", methods=["POST"])
def processing():
    """Return a processing page, to show progress updated from the api."""
    global process_status
    process_status = ProcessStatus()
    global path_summary_request
    path_summary_request = req.PathSummaryRequest(request)

    result = path_summary_request.validate()

    Thread(target=finding_path,
           args=path_summary_request.to_find_path()).start()

    return result.html()


def finding_path(start_stop_code,
                 end_stop_code,
                 criteria):
    """Find path, redirects to results when finished."""

    graph = Graph()
    process_status.set_status("Creating bus routes graph", main_status=True)
    graph.create_graph()

    path_lists = search_path(
        start_stop_code, end_stop_code, graph, process_status=process_status)
    paths_summary = sort_paths(
        path_lists, criteria, process_status=process_status)

    path_summary_request.set_paths_summary(paths_summary.data, summarise=True)
    process_status.status_done = True


@app.route("/paths_summary")
def paths_summary():
    """Return the results page."""
    return path_summary_request.handle().html()


@app.route("/path_info")
def path_info():
    """Return detailed information on a path.

    If path is not found, redirect back to home page.
    If distance does not match, return all paths.
    """
    return req.PathInfoRequest(request).handle().html()


@app.route("/api/v1/status")
def status():
    """To return status of the run."""
    return process_status.jsonify()


@app.route("/api/v1/allbusstopinfo")
def info():
    all_bus_stop_info = list(bu.retrieve_all_bus_stops().values())
    for i in range(len(all_bus_stop_info)):
        all_bus_stop_info[i]["id"] = i

    return jsonify(all_bus_stop_info)


app.run(host=host, port=port, debug=True)
