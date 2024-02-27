from abc import ABC, abstractmethod


class TermAttr(ABC):

    @abstractmethod
    def vos(self,sCls):
        pass
    @abstractmethod
    def vosOcc(self,sCls):
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