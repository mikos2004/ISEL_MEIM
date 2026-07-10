from lib.ref.memoria_experiencia import MemoriaExperiencia
from lib.ref.q_learning import QLearning


class QME(QLearning):
    """
    QLearning com Memória de Experiência. Extende do QLearning base, usando-o por base    
    """
    def __init__(self, mem_aprend, sel_accao, alfa, gama, num_sim, dim_max):
        super().__init__(mem_aprend, sel_accao, alfa, gama)
        self.__num_sim = num_sim
        self.__memoria_experiencia = MemoriaExperiencia(dim_max)

    def aprender(self, s, a, r, sn):
        # aprendizagem normal do QLearning
        super().aprender(s, a, r, sn)

        # guardar experiência
        e = (s, a, r, sn)
        self.__memoria_experiencia.atualizar(e)

        # aprender com a simulação
        self.simular()

    def simular(self):
        # obter amostras da memória
        amostras = self.__memoria_experiencia.amostrar(self.__num_sim)

        # aprender sobre cada amostra
        for (s, a, r, sn) in amostras:
            super().aprender(s, a, r, sn)
