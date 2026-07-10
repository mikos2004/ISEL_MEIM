import random

class MemoriaExperiencia:
    def __init__(self, dim_max):
        self.__dim_max = dim_max
        self.__memoria = []

    def atualizar(self, e):
        # Se atingirmos a dimensão máxima, remove-se o elemento mais antigo
        if len(self.__memoria) == self.__dim_max:
            self.__memoria.pop(0)
        # guardar a expriência
        self.__memoria.append(e)

    def amostrar(self, n):
        """Obter n amostras da memória

        Args:
            n: n amostras

        Returns:
            lista com amostras
        """
        n_amostras = min(n, len(self.__memoria))
        return random.sample(self.__memoria, n_amostras)
