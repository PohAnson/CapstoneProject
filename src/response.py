from flask import render_template


class Result:
    def __init__(self):
        raise NotImplementedError

    def html(self):
        raise NotImplementedError


class ResultError(Result):
    def __init__(self, message) -> None:
        self.message = message

    def html(self):
        return f"<h1>result error</h1><p>{self.message}</p>"


class ProcessingSuccess(Result):
    def __init__(self):
        pass

    def html(self):
        return render_template("processing.html")


class PathSummarySuccess(Result):
    def __init__(self, path_summary):
        self.path_summary = path_summary

    def html(self):
        return render_template("paths_summary.html",
                               path_summary=self.path_summary)


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
