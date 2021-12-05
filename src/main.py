"""File to start the flask app."""
from flask import Flask, render_template, request, redirect, session, jsonify
import bus_utils as bu
from graph import Graph
from webui import WebInterface
from validation import validate_stops
from pathfinding import sort_paths, search_path
from flask_cors import CORS
from config import host, port
from webui import ProcessStatus, WebInterface

app = Flask(__name__)
app.secret_key = "098765456789"
CORS(app)

ui = WebInterface()
all_results = []


@app.route("/")
def root():
    """Return page containing the form."""
    return render_template("index.html", ui=ui)


@app.route("/processing", methods=["POST"])
def processing():
    """Return a processing page, to show progress updated from the api."""
    global process_status
    process_status = ProcessStatus()
    ui.clear_error_message()

    start_stop_code = request.form.get("start_stop_code", None)
    end_stop_code = request.form.get("end_stop_code", None)
    criteria = request.form.get("criteria", None)

    if None in (start_stop_code, end_stop_code, criteria):
        ui.set_error_message("There is no input for starting stop code")
        return redirect("/")
    elif not validate_stops(start_stop_code, end_stop_code):
        ui.set_error_message("Invalid bus stop code is given")
        return redirect("/")

    session["start_stop_code"] = start_stop_code
    session["end_stop_code"] = end_stop_code
    session["criteria"] = criteria

    return render_template(
        "processing.html",
        ui=ui,
    )


@app.route("/finding_path")
def finding_path():
    """Find path, redirects to results when finished."""
    global all_results

    all_results = []
    ui.clear_status()
    start_stop_code = request.args.get("start_stop_code", session["start_stop_code"])
    end_stop_code = request.args.get("end_stop_code", session["end_stop_code"])
    criteria = request.args.get("criteria", session["criteria"])

    graph = Graph()
    process_status.set_status("Creating bus routes graph", main_status=True)
    graph.create_graph()

    path_lists = search_path(
        start_stop_code, end_stop_code, graph, process_status=process_status)
    paths_summary = sort_paths(
        path_lists, criteria, process_status=process_status)

    process_status.status_done = True


@app.route("/paths_summary")
def paths_summary():
    """Return the results page."""
    return render_template("paths_summary.html", ui=ui)


@app.route("/path_info")
def path_info():
    """Return detailed information on a path.

    If path is not found, redirect back to home page.
    If distance does not match, return all paths.
    """
    ui.clear_detailed_path_results()
    path_list = [request.args.get("path", "").split(" ")]
    dist = request.args.get("distance", "")

    paths = sort_paths(path_list, "dist")
    if len(paths) == 0:
        return redirect("/")
    ui.set_detailed_path_results([path for path in paths if str(path["dist"]) == dist])
    if ui.get_detailed_path_results() == []:
        ui.set_detailed_path_results(paths)

    readable_path = f" {chr(0x1f86a)} ".join(
        [
            bu.get_bus_stop_info(stop_code)["description"]
            for stop_code in paths[0]["path"]
        ]
    )
    return render_template("detailed_info.html", readable_path=readable_path, ui=ui)


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
