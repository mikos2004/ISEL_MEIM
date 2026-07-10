# teste_cozinha_minimal.py
from accao import AccaoCozinha
from ambiente import AmbienteCozinha
from agente_aprend_ref import AgenteAprendRef
from lib.ref.mec_aprend_ref import MecAprendRef

# Parâmetros de teste
num_episod = 100
epsilon = 0.1

# Iniciar ambiente e agente
ambiente = AmbienteCozinha()
accoes = list(AccaoCozinha)
mec_aprend_ref = MecAprendRef(accoes, epsilon)
agente = AgenteAprendRef(ambiente, mec_aprend_ref)

# Executar agente
num_passos_episodio = agente.executar(num_episod)

# Mostrar política aprendida
ambiente.mostrar_politica(mec_aprend_ref.obter_politica())
ambiente.mostrar_valor(mec_aprend_ref.obter_valor())

# Mostrar número de passos por episódio
print(f"\nPassos por episódio: {num_passos_episodio}")
min_passos = min(num_passos_episodio)
print(f"\nMinimo de passos: {min_passos} no EP: {num_passos_episodio.index(min_passos) + 1}")