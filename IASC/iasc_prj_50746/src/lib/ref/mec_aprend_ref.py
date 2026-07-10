from lib.ref.e_greedy import EGreedy
from lib.ref.memoria_esparsa import MemoriaEsparsa
from lib.ref.q_learning import QLearning
from lib.ref.qme import QME
from lib.ref.aprendizagem import Aprendizagem

# alpha = 0.5
# gama = 0.9

"""Mecanismo de Aprendizagem por Reforço

Classe que representa um mecanismo de aprendizagem por reforço, que utiliza
vários tipos de memórias, mecanismos de seleção de ação e algoritmos de
aprendizagem de reforço, desde que sejam desenvolvidos de forma compatível com
a arquitetura presente. 
"""

class MecAprendRef(Aprendizagem):
    
    def __init__(self, accoes, epsilon=None):
        self.__accoes = accoes
        self.__mem_aprend = MemoriaEsparsa()
        self.__sel_accao = EGreedy(self.__mem_aprend, self.__accoes, epsilon)
        #self.__aprend_ref = QLearning(self.__mem_aprend, self.__sel_accao, 0.5, 0.9)
        
        # amb7x1
        #self.__aprend_ref = QME(self.__mem_aprend, self.__sel_accao, 0.5, 0.9, 100, 1000)
        
        # problema cozinha
        self.__aprend_ref = QME(self.__mem_aprend, self.__sel_accao, 0.5, 0.9, 200, 5000)
        #self.__aprend_ref = QME(self.__mem_aprend, self.__sel_accao, 0.5, 0.9, 100, 1000)

    
    def aprender(self, s, a, r, sn, an=None):
        self.__aprend_ref.aprender(s, a, r, sn)
    
    def selecionar_accao(self, s):
        return self.__sel_accao.selecionar_accao(s)
    
    def obter_politica(self):
        politica = {}
        for s in self.__mem_aprend.obter_estados():
            politica[s] = self.__sel_accao.max_accao(s)
        return politica
    
    def obter_valor(self):
        valor = {}
        for s in self.__mem_aprend.obter_estados():
            # o valor do estado é o valor da estimativa do estado-ação Q(s,a) quando a ação é a que maximiza o valor do estado
            valor[s] = self.__mem_aprend.Q(s, self.__sel_accao.max_accao(s))
        return valor