"""Data structure and Algorithm to help with sorting."""


from typing import Dict, Iterable, Sequence, TypeVar

_KT = TypeVar('_KT')
_VT = TypeVar('_VT', str, int)


class OrderedList(Sequence[Dict[_KT, _VT]]):
    """
    Ensure that data is always ordered to help insert data quickly
    via binary search.

    Contains a list of iterables
    """

    def __init__(self, index: _KT) -> None:
        """Initialise the list with a criteria to sort by.

        Args:
            index (str/int): The index/criteria to sort the list by.
        """
        self.__data: list[Dict[_KT, _VT]] = []
        self.index: _KT = index

    def __repr__(self) -> str:
        """
        Representation of self.

        Returns:
            str: Shows data it is initialised with

        """
        return str(self.__data)

    def __str__(self) -> str:
        """
        Convert self to a string.

        Returns:
            str: Shows data it is initialised with

        """
        return str(self.__data)

    def __getitem__(self, index: int) -> Dict[_KT, _VT]:
        """
        Get item of the OrderedList at a specified index.

        Args:
            index (int): Index position in data.

        Returns:
            dictionary/iterable: A single element in the data.

        """
        return self.__data[index]

    def __len__(self) -> int:
        """Return the length of the data."""
        return len(self.__data)

    @ property
    def data(self) -> list[Dict[_KT, _VT]]:
        return self.__data

    @ data.setter
    def data(self, datas: Iterable) -> None:
        self.__data.clear()
        for data in datas:
            self.insert(data)

    def insert(self, value: Dict[_KT, _VT]) -> None:
        """Insert value into the list.

        Args:
            value (dict): the value to insert into ordered list.
        """

        # edge case where data is empty
        if len(self.__data) == 0:
            self.__data.append(value)

        else:
            # binary search the place to insert
            lo = 0
            hi = len(self.__data)

            while lo < hi:
                mid = (hi + lo) // 2
                if value[self.index] < self.__data[mid][self.index]:
                    hi = mid
                else:
                    lo = mid + 1
            self.__data.insert(hi, value)
