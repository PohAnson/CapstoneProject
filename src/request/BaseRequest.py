from abc import ABC, abstractmethod

from response import Result


class Request(ABC):
    def __init__(self, flask_request):
        self.flask_request = flask_request

    @abstractmethod
    def handle(self) -> Result:
        raise NotImplementedError
