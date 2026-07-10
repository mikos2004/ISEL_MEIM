from rna.rede.rede_neuronal import RedeNeuronal
from rna.activacao.tanh import TanH
import matplotlib.pyplot as plt

# Dados de treino e de teste
entradas = [[0, 0], [0, 1], [1, 0], [1, 1]]
saidas = [[0], [1], [1], [0]]

# Parâmetros de estudo
FORMA = [2, 2, 1]
TAXA_APREND = 0.2
MOMENTO = 0.01
EPOCAS = 1000
ERRO_MAX = 0.05
FUNC_ACTIV = TanH()

# Configurar rede
rede = RedeNeuronal(FORMA, FUNC_ACTIV)

# Treinar rede
hist_erros = rede.treinar(entradas, saidas, EPOCAS, ERRO_MAX, TAXA_APREND, MOMENTO)

# Prever após treino
previsao = rede.prever(entradas)

print(previsao)


"""plt.plot(hist_erros)
plt.xlabel('Época')
plt.ylabel('Erro máximo')
plt.title('Progresso do Treino da Rede Neuronal')
plt.show()"""