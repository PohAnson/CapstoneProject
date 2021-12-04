"""Data structure and Algorithm to help with sorting."""


class OrderedList:
    """
    Ensure that data is always ordered to help insert data quickly via binary search.

    Contains a list of iterables
    """

    def __init__(self, index):
        """Initialise the list with a criteria to sort by.

        Args:
            index (str/int): The index/criteria to sort the list by.
        """
        self.data = []
        self.index = index

    def __repr__(self):
        """
        Representation of self.

        Returns:
            str: Shows data it is intialised with

        """
        return str(self.data)

    def __str__(self):
        """
        Convert self to a string.

        Returns:
            str: Shows data it is intialised with

        """
        return str(self.data)

    def __getitem__(self, index):
        """
        Get item of the OrderedList at a specified index.

        Args:
            index (int): Index position.

        Returns:
            dictionary/iterable: A single element in the data.

        """
        return self.data[index]

    def __len__(self):
        """Return the length of the data."""
        return len(self.data)

    def insert(self, value):
        """Insert value into the list.

        Args:
            value ([dict]): [description]
        """
        index = self.index
        if len(self.data) == 0:
            self.data.append(value)
        elif value[index] < self.data[0][index]:
            self.data.insert(0, value)

        elif value[index] >= self.data[-1][index]:
            self.data.append(value)
        else:
            target_found = False
            left = 0
            right = len(self.data)

            while not target_found:
                mid = (right + left) // 2
                if value[index] < self.data[mid][index]:
                    right = mid
                elif self.data[mid][index] <= value[index] <= self.data[mid + 1][index]:
                    self.data.insert(mid + 1, value)
                    target_found = True
                else:
                    left = mid + 1
