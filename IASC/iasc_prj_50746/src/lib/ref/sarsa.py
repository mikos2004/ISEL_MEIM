from lib.ref.aprend_ref import AprendRef


class SARSA(AprendRef):

    def aprender(self, s, a, r, sn, an=None):
        qsa = self._mem_aprend.Q(s, a)
        qsnan = self._mem_aprend.Q(sn, an)
        q = qsa + self._alfa * (r + self._gama * qsnan - qsa)
        self._mem_aprend.atualizar(s, a, q)