from lib.ref import sel_accao
from lib.ref.aprend_ref import AprendRef


class QLearning(AprendRef):
    """Algoritmo QLearning

    Algoritmo onde a estimativa de retorno R (valor estimado de 
    realizar a acção "a" num estado "s") considerando a acção "a'" 
    correspondente à melhor estimativa Q(s',a')
    """

    def aprender(self, s, a, r, sn):
        # em vez de receber o an (ação a executar) como SARSA
        # o QLearning calcula-o selecionanda aquela que
        # maximiza a respetiva estimativa do valor max_accao(Q(s, a'))
        an = self._sel_accao.max_accao(sn)
        qsa = self._mem_aprend.Q(s, a)
        qsnan = self._mem_aprend.Q(sn, an)
        # atualizar Q
        q = qsa + self._alfa * (r + self._gama * qsnan - qsa)
        # atualizar a memoria aprendida e atualizar "s"
        self._mem_aprend.atualizar(s, a, q)