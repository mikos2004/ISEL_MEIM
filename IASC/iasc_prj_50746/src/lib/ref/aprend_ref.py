from abc import ABC, abstractmethod

"""AprendRef

Interface para implementar algoritmos de Aprendizagem por Reforço
"""
class AprendRef(ABC):

    def __init__(self, mem_aprend, sel_accao, alfa, gama):
        self._mem_aprend = mem_aprend
        self._sel_accao = sel_accao
        self._alfa = alfa
        self._gama = gama
    
    @abstractmethod
    def aprender(self, s, a, r, sn, an=None):
        raise ValueError('Ainda não foi implementado.')