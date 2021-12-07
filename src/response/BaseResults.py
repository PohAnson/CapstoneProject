from abc import ABC, abstractclassmethod


class Result(ABC):
    def __init__(self):
        raise NotImplementedError

    @abstractclassmethod
    def html(self):
        raise NotImplementedError


class ResultError(Result):
    def __init__(self, message) -> None:
        self.message = message

    def html(self):
        return f"<h1>result error</h1><p>{self.message}</p>"
