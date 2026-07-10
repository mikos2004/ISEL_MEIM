from abc import ABC, abstractmethod

"""Interfce Memoria Aprendida

Representa a memoria aprendida
"""
class MemoriaAprend(ABC):
    
    @abstractmethod
    def atualizar(self, s, a, q):
        """Atualiza o valor Q para o par (s, a) com o novo valor Q"""
        raise ValueError('Ainda não foi implementado.')
    
    @abstractmethod
    def Q(self, s, a):
        """Retorna o valor Q atual para o par estado-ação (s, a)"""
        raise ValueError('Ainda não foi implementado.')