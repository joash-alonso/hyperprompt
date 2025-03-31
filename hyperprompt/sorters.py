from abc import ABC, abstractmethod

class Sorter(ABC):

    @abstractmethod
    def sort(self) -> None:
        ...

class TopologicalSorter(Sorter):
    ...
