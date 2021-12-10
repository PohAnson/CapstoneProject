"""Contains Bus to allow for quick comparison."""


class Bus:
    __created_buses = {}  # (service_no, direction, stop_sequence): Bus

    def __init__(self,
                 service_no: str,
                 direction: int,
                 stop_sequence: int) -> None:
        self.service_no: str = service_no
        self.direction: int = direction
        self.stop_sequence: int = stop_sequence

    def __new__(cls, *args):
        if args not in cls.__created_buses.keys():
            cls.__created_buses[args] = object.__new__(cls)
        return cls.__created_buses[args]

    def __repr__(self) -> str:
        return ("Bus("
                f"{self.service_no}, "
                f"{self.direction}, "
                f"{self.stop_sequence}, "
                f"{self.__hash__()}"
                ")"
                )

    def __hash__(self) -> int:
        return hash(self.service_no) >> hash(self.direction)

    def __eq__(self, __o: "Bus") -> bool:
        # Same bus if the service no and direction is same.
        return (self.service_no == __o.service_no
                and self.direction == __o.direction)

    # gt, lt compares the stop sequence
    def __gt__(self, __o):
        return self.stop_sequence > __o.stop_sequence

    def __lt__(self, __o):
        return self.stop_sequence < __o.stop_sequence
