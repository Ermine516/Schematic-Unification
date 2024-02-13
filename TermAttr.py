from abc import ABC, abstractmethod


class TermAttr(ABC):
    @abstractmethod
    def recs(self):
        pass
    @abstractmethod
    def vars(self):
        pass
    @abstractmethod
    def varsOcc(self):
        pass
    @abstractmethod
    def recsOcc(self):
        pass
    @abstractmethod
    def maxIdx(self):
        pass
    @abstractmethod
    def minIdx(self):
        pass
    @abstractmethod
    def occurs(self,t):
        pass
    @abstractmethod
    def depth(self):
        pass
    @abstractmethod
    def instance(self):
        pass
    @abstractmethod
    def applyFunc(self,f):
        pass