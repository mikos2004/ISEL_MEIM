from abc import ABC, abstractmethod

class Aprendizagem(ABC):
    
    @abstractmethod
    def selecionar_accao(self, s):
        raise ValueError('Ainda não foi implementado.')
    
    @abstractmethod
    def aprender(self, s, a, r, sn, an=None):
        raise ValueError('Ainda não foi implementado.')