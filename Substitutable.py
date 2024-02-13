from abc import ABC, abstractmethod

class Substitutable(ABC):
    @abstractmethod
    def handleSubstitution(self,sigma):
        pass