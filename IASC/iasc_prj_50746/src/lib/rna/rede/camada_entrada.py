"""
Camada de Entrada

Representa a camada de entrada de uma rede neural.
Ela regista e disponibiliza os dados de entrada
"""
class CamadaEntrada:
    def __init__(self, d_s):
        """Construtor CamadaEntrada

        Args:
            d_s : dimensão de saída (nº de saídas da camada)
        """
        self.d_s = d_s
        self.y = [0 for _ in range(d_s)]  # Vector de saída inicializado com zeros
    
    def propagar(self, x):
        """Propagar entrada gerando a saída da camada

        Visto que, y é equivalente a x e que os neurónios
        implementam a função identidade f(xi) = xi

        y = f(xi) = xi

        Portanto: self.y = x
        
        Args:
            x: Vetor de entrada

        Returns:
            y: Vetor e saída
        """
        self.y = x # mantém-se a informação de saída
        return self.y