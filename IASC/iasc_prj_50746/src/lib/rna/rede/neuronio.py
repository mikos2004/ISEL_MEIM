import random

from rna.activacao.activacao import Activacao

"""
Neuronio

Unidade computacional que opera no dominio dos valores reais. 
Faz um produto interno das entradas com os pesos das ligações 
para produzir uma saída.
"""
class Neuronio:
    def __init__(self, d, phi : Activacao):
        # d: Dimensão de entrada (número ligações de entrada do neuronio)
        # phi: Função de activação - recebe um valor real "h" e produz um valor real "y" que é a resposta produzida. Determina a fronteira de discriminação.
        self.phi = phi # Ativacao
        self.w = [random.choice([-1, 1]) for i in range(d)]  # Vector de pesos: apenas -1 ou 1
        self.b = random.choice([-1, 1])  # Pendor interno: apenas -1 ou 1
        self.delta_w = [0 for i in range(d)]  # Vector de variação dos pesos
        self.delta_b = 0  # Variação do pendor
        self.h = 0  # Soma da activação das entradas
        self.y = 0  # Saída do neurónio
        self.y_l = 0 # Derivada da saída do neurónio (y′)


    def propagar(self, x):
        # x: vector de entradas
        # Produto interno entre x e w
        self.h = sum(xi * wi for xi, wi in zip(x, self.w)) + self.b
        self.y = self.phi.f(self.h)
        # Calcula a derivada da função de ativação
        self.y_l = self.phi.df(self.h)
        return self.y
    
    def adaptar(self, delta, y_ant, alpha, beta):
        """
        Adaptar pesos das ligações de entrada e pendor interno para ser usado pela camada

        Args:
            delta: Componente de propagação do erro de saída do neurónio
            y_ant: Vector de saída da camada anterior n-1
            alpha: Taxa de aprendizagem
            beta: Factor de momento
        """

        # Atualizar cada peso individualmente
        for i in range(len(self.w)):
            # Momento dos pesos
            M_w = beta * self.delta_w[i]

            # variação do peso
            #delta_w_i = -alpha * self.y_l * delta * y_ant[i] + M_w
            self.delta_w[i] = -alpha * self.y_l * delta * y_ant[i] + M_w

            # Atualiza o peso
            self.w[i] += self.delta_w[i]

        # Momento do pendor
        M_b = beta * self.delta_b
        
        # Variação do pendor
        delta_b = -alpha * self.y_l * delta + M_b
        
        # Atualizar pendor
        self.delta_b = delta_b
        self.b += self.delta_b