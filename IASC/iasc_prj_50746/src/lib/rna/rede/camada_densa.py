from lib.rna.activacao.activacao import Activacao
from lib.rna.rede.neuronio import Neuronio


class CamadaDensa:
    
    def __init__(self, d_e, d_s, phi):
        """Construtor Camda densa

        Args:
            d_e : Dimensão de entrada
            d_s : Dimensão de saída
            phi : Função de Ativação
        """
        self.d_e = d_e
        self.d_s = d_s
        self.phi = phi
        self.neuronios = [Neuronio(d_e, phi) for i in range(d_s)] # neuronios da camada

    def propagar(self, x):
        """Propagar sinal de entrada, por cada camada, gerando a saída da camadda

        Args:
            x: Vetor de entrada

        Returns:
            y: Vetor e saída
        """
        y = [neuronio.propagar(x) for neuronio in self.neuronios]
        return y
    

    def adaptar(self, delta_n, y_ant, alpha, beta):
        """Adaptar pesos e pendores dos neurónios da camada

        Args:
            delta_n: Vector de erro de saída da camada n
            y_ant: Vector de saída da camada anterior n-1
            alpha: Taxa de aprendizagem
            beta: Factor de momento
        """
        # Para cada neurónio j na camada atual
        for j in range(self.d_s):
            # delta_j_n: Componente j do vector de erro de saída da camada n
            delta_j_n = delta_n[j]
            # Chama o método adaptar do neurónio j
            self.neuronios[j].adaptar(delta_j_n, y_ant, alpha, beta)

    @property
    def y(self):
        """
        Devolve as saídas atuais dos neurónios.
        
        Returns:
            Lista de saídas dos neurónios
        """
        return [neuronio.y for neuronio in self.neuronios]