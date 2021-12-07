from flask import jsonify


class ProcessStatus:
    def __init__(self) -> None:
        self.status_done = False
        self.main_status = ""
        self.sub_status = ""

    def set_status(self, status, main_status=False):
        """Update the status.

        Args:
            status (str): The status message to update
            main_status (bool, optional): Whether it is the main status.
                Defaults to False.
        """
        if not main_status:
            self.sub_status = status
        else:
            self.main_status = status

    def clear_status(self):
        """Clear all the status message."""
        self.main_status = ""
        self.sub_status = ""

    def jsonify(self):
        return jsonify({"status_done": self.status_done,
                        "main_status": self.main_status,
                        "sub_status": self.sub_status, })
