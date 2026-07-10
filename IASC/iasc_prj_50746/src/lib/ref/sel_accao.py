from abc import ABC, abstractmethod

class SelAccao(ABC):
    
    def __init__(self, mem_aprend):
        self._mem_aprend = mem_aprend
    
    @abstractmethod
    def selecionar_accao(self, s):
        raise ValueError('Ainda não foi implementado.')
    
    @abstractmethod
    def max_accao(self, s):
        raise ValueError('Ainda não foi implementado.')