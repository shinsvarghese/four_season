from abc import ABCMeta, abstractmethod
from abc import ABCMeta, abstractmethod

class MapperInterface:
    __metaclass__ = ABCMeta

    @abstractmethod
    def getData(self):
        None

    @abstractmethod
    def performUpdate(self):
        None