from abc import ABC, abstractmethod

"""
Inteface que representa uma função de ativação
"""
class Activacao(ABC):

    @abstractmethod
    def f(self, x):
        """
        # y = ?
        return y
        """
    
    @abstractmethod
    def df(self, x):
        """
        # dy = ?
        return dy
        """