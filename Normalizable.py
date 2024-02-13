from abc import ABC, abstractmethod


class Normalizable(ABC):
    @abstractmethod
    def normalize(self):
        pass