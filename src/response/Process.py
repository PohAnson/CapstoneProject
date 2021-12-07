from flask import render_template

from .BaseResults import Result


class ProcessingSuccess(Result):
    def __init__(self):
        return

    def html(self):
        return render_template("processing.html")


class PathSummarySuccess(Result):
    def __init__(self, path_summary):
        self.path_summary = path_summary

    def html(self):
        return render_template("paths_summary.html",
                               path_summary=self.path_summary)
