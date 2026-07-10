from lib.rna.rede.camada_densa import CamadaDensa
from lib.rna.rede.camada_entrada import CamadaEntrada

"""
Rede Neuronal

Representa uma rede neural com múltiplas camadas.
A primeira camada é sempre uma Camada de Entrada.
As camadas subsequentes são Camadas Densas.
"""
class RedeNeuronal:
    def __init__(self, forma, phi):
        """Construtor Rede Neuronal

        Args:
            forma: Lista de número de neurónios por camada
            phi: Função de activação
        """
        self.forma = forma  # Forma da rede
        self.phi = phi      # Função de activação
        self.N = len(forma)  # Número de camadas

        self.camadas = []
        
        # Camada de Entrada
        d_s_1 = forma[0]
        camada_1 = CamadaEntrada(d_s_1)
        self.camadas.append(camada_1)

        # as restantes Camadas são Densas
        for n in range(1, self.N):
            # d_e_n -> saída da camada anterior
            d_e_n = forma[n-1]
            # d_s_n = número de neurónios nesta camada
            d_s_n = forma[n]
            camada_n = CamadaDensa(d_e_n, d_s_n, phi)
            self.camadas.append(camada_n)
    

    def delta_saida(self, y_N, y):
        """Calcula o erro de saída da rede"""
        return [y_N_k - y_k for y_N_k, y_k in zip(y_N, y)]
    

    def retropropagar(self, delta_N, alpha, beta):
        """Retropropagar erro pelas camadas da rede, excepto a camada de entrada

        - O algoritmo de retropropagação usa o cálculo dos gradientes da função
            de perda necessários para atualizar os parâmetros do modelo (rede neuronal)
        - O objetivo é minimizar o erro de previsão

        Args:
            delta_N: Vector de variação de erro de saída da rede
            alpha: Taxa de aprendizagem
            beta: Factor de momento
        """
        delta_n = delta_N
        
        # Camada de entrada apenas mantém entradas
        for n in range(self.N - 1, 0, -1):
            # ant = n-1
            # atual = n
            y_ant = self.camadas[n - 1].y
            # Dimensão da camada n - 1
            d_ant = self.camadas[n - 1].d_s
            # Dimensão da camada n
            d_atual = self.camadas[n].d_s
            # Neurónios da camada n
            neuronios = self.camadas[n].neuronios
            
            
            delta_ant = []
            for i in range(d_ant): 
                soma = 0
                for j in range(d_atual):
                    neur_j = neuronios[j]
                    w_i = neur_j.w[i]
                    # delta_n_j -> Componente j do vector de variação 
                    #               de erro de saída para cada camada
                    soma += w_i * delta_n[j] * neur_j.y_l
                delta_ant.append(soma)
            
            self.camadas[n].adaptar(delta_n, y_ant, alpha, beta)
            delta_n = delta_ant

    def adaptar(self, x, y, alpha, beta):
        """Adaptar parâmetros da rede

        Args:
            x: Vector de treino de entrada
            y: Vector de treino de saída
            alpha: Taxa de aprendizagem
            beta: Factor de momento

        Returns:
            epsilon: Erro médio de saída da rede
        """
        # Vector de saída gerado pela rede
        y_N = self.propagar(x)
        
        # Vector de variação de erro de saída
        delta_N = self.delta_saida(y_N, y)
        
        # retropropagar o erro ao longo das várias camadas da rede
        self.retropropagar(delta_N, alpha, beta)
        
        # Dimensão do vector de perda
        K = len(delta_N)
        
        # Erro médio de saída da rede
        epsilon = (1 / K) * sum(delta_k ** 2 for delta_k in delta_N)
        
        return epsilon
    

    def treinar(self, X, Y, n_epocas, epsilon_max, alpha, beta):
        """Treinar a rede neuronal

        Args:
            X: Conjunto de entradas x
            Y: Conjunto de saídas y
            n_epocas: Número de épocas de treino
            epsilon_max: Erro máximo aceitável
            alpha: Taxa de aprendizagem
            beta: Factor de momento
        """
        historico = []

        for epoca in range(n_epocas):
            epsilon = 0
            
            for x, y in zip(X, Y):
                # erro de treino por entrada x
                epsilon_x = self.adaptar(x, y, alpha, beta)
                
                # mantém o maior erro na época
                if epsilon_x > epsilon:
                    epsilon = epsilon_x
            
            # Valores
            historico.append(epsilon)
            
            # Se o erro for menor ou igual ao máximo, acaba o treino
            if epsilon <= epsilon_max:
                return historico
        
        return historico
            
    def prever(self, X):
        """Prever saídas para um conjunto de entradas

        Args:
            X: Conjunto de vectores de entrada

        Returns:
            Y: Conjunto de vectores de saída
        """
        Y = [self.propagar(x) for x in X]
        return Y
    
            
    def propagar(self, x):
        """Propagar saída para uma dada entrada

        Args:
            x: Vector de entrada

        Returns:
            y: Vector de saída da rede
        """
        y = x
        
        # Propaga através de todas as camadas
        for camada in self.camadas:
            y = camada.propagar(y)
        
        return y