from flask import render_template

from .BaseResults import Result


class PathInfoSuccess(Result):
    def __init__(self, action, message=None):
        self.action = action
        self.message = message
        self.detailed_path = []
        self.readable_path = ''

    def html(self):
        return render_template("detailed_info.html",
                               readable_path=self.readable_path,
                               path_info=self.detailed_path)

    def get_detailed_path_results(self):
        """Get the results for the details of a path.

        Returns:
            list: contains DetailedPathResult object
        """
        return self.detailed_path

    def set_detailed_path_results(self, result):
        self.detailed_path = result

    def clear_detailed_path_results(self):
        """Clear all the detailed results."""
        self.detailed_path = []
