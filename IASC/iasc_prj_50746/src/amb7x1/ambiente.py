from accao import Accao

"""Ambiente 7x1

Classe que define o ambiente 7x1 para teste da aprendizagem por reforço
"""

class Ambiente:
    def __init__(self, posicao_inicial, r_max=1):
        """Construtor do Ambiente 7x1

        Args:
            posicao_inicial: posição inicial
            r_max: reforço máximo
        """
        # chars que delimitam e representam o ambiente e os seus elementos
        self.ambiente = ['-', '.', '.', '.', '.', '.', '+']
        # posição do agente
        self.posicao_agente = posicao_inicial
        # guardar a Pos Inicial ajuda a reiniciar o ambiente
        self.posicao_inicial = posicao_inicial
        # reforço máximo
        self.r_max = r_max

    # @property permite transformar um método de classe num atributo
    @property
    def dim_amb(self):
        """dimensão do ambiente

        Returns:
            tamanho do ambiente
        """
        return len(self.ambiente)
    
    def reiniciar(self):
        """Reiniciar

        Returns:
            posicao do agente
        """
        # move o agente para a sua pos inicial
        self.mover_agente(self.posicao_inicial)
        return self.posicao_agente
    
    def actuar(self, accao):
        """actuar

        Args:
            accao: ação a executar
        """
        posicao = self.posicao_agente
        if accao == Accao.ESQ:
            posicao -= 1
        elif accao == Accao.DIR:
            posicao += 1
        
        if posicao >= 0 and posicao < self.dim_amb:
            self.mover_agente(posicao)
    
    def observar(self):
        """observar

        Returns:
            posição do agente, reforço consoante a posição
        """
        return self.posicao_agente, self.reforco(self.posicao_agente)
    
    def mover_agente(self, posicao):
        """mover agente

        atualiza posição do agente

        Args:
            posicao do agente
        """
        self.posicao_agente = posicao
    
    def reforco(self, posicao):
        """Reforço

        Args:
            posicao: posição do agente

        Returns:
            valor do reforço
        """
        # obtem o elemento do ambiente
        elemento = self.ambiente[posicao]
        if elemento == '+':
            r = self.r_max # recompensa desempenho
        elif elemento == '-':
            r = -self.r_max # penaliza desempenho
        else:
            r = 0
        return r
    
    def mostrar(self):
        """mostrar ambiente
        """
        for posicao in range(self.dim_amb):
            # percorrer o amb e mostrar o agente com um A
            if posicao == self.posicao_agente:
                print('A', end='')
            else:
                # mostrar o resto do amb com respetivo elemento
                print(self.ambiente[posicao], end='')
        print()
    
    def mostrar_politica(self, politica):
        """Mostrar politica

        Args:
            politica: dicionário da politica, resultante da aprendizagem
        """
        print("\nPolítica:")
        for s in range(self.dim_amb):
            # obter politica para cada estaddo
            accao = politica.get(s)
            print(accao, end=' ')
        print()
    
    def mostrar_valor(self, valor):
        """Mostrar valor do estado

        Args:
            valor: lista com os valores de cada estado
        """
        print("\nValor:")
        for s in range(self.dim_amb):
            # valor é calculado, optando-se pelo maior valor para as várias ações possiveis
            vs = valor.get(s)
            print(f"{vs}", end=' ')
        print()
    
