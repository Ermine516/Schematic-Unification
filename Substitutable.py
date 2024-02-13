from abc import ABC, abstractmethod


class Domainable(ABC):
    pass

class Substitutable(ABC):
    @abstractmethod
    def handleSubstitution(self,sigma):
        pass