from response import AllStopInfoResult

from .BaseRequest import Request


class AllStopInfoRequest(Request):
    def handle(self) -> AllStopInfoResult:
        return AllStopInfoResult()
