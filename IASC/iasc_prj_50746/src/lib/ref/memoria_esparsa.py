from lib.ref.memoria_aprend import MemoriaAprend


class MemoriaEsparsa(MemoriaAprend):
    def __init__(self, valor_omissao=0.0):
        self.__valor_omissao = valor_omissao
        self.__memoria = {}
        self.__estados = set()
    
    def Q(self, s, a):
        # Provoca o auto-arranque
        return self.__memoria.get((s, a), self.__valor_omissao)
    
    def atualizar(self, s, a, q):
        self.__memoria[(s, a)] = q
        self.__estados.add(s)

    def obter_estados(self):
        return self.__estados