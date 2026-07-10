import random
from lib.ref.sel_accao import SelAccao


class EGreedy(SelAccao):
    def __init__(self, mem_aprend, accoes, epsilon):
        super().__init__(mem_aprend)
        self.__epsilon = epsilon
        self.__accoes = accoes
    
    def selecionar_accao(self, s):
        if random.random() > self.__epsilon:
            accao = self.aproveitar(s)
        else:
            accao = self.explorar()
        return accao
    
    def aproveitar(self, s):
        """Aproveitar

        Args:
            s: estado

        Returns:
            _type_: _description_
        """
        return self.max_accao(s)
    
    def explorar(self):
        """Explroar

        Returns:
            Retorna uma ação a explorar, escolhida aleatoriamente
        """
        return random.choice(self.__accoes)

    def max_accao(self, s):
        """Max Ação

        Args:
            s: estado

        Returns:
            Ação cujo valor Q é máximo
        """
        accoes_shuffle = self.__accoes.copy()
        random.shuffle(accoes_shuffle)
        return max(accoes_shuffle, key=lambda a: self._mem_aprend.Q(s, a))