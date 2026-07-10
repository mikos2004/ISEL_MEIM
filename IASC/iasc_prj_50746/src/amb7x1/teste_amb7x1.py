import sys
import os

# DEBUG: Mostra o que está no Python path
# print("Python path antes:")
# for path in sys.path:
#     print(f"  {path}")

# Adiciona o caminho absoluto aos PYTHONPATH
#root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
#sys.path.insert(0, root_path)

#print(f"Adicionado: {root_path}")
#print("Python path depois:")
#for path in sys.path:
#    print(f"  {path}")

from accao import Accao
from agente_aprend_ref import AgenteAprendRef
from ambiente import Ambiente
from lib.ref.mec_aprend_ref import MecAprendRef


# Parâmetros de teste
posicao_inicial = 3
num_episod = 50
epsilon = 0.1

# Iniciar ambiente e agente
ambiente = Ambiente(posicao_inicial)
accoes = list(Accao)
mec_aprend_ref = MecAprendRef(accoes, epsilon)
agente = AgenteAprendRef(ambiente, mec_aprend_ref)

# Executar agente
num_passos_episodio = agente.executar(num_episod)

# Mostrar política aprendida
ambiente.mostrar_politica(mec_aprend_ref.obter_politica())
ambiente.mostrar_valor(mec_aprend_ref.obter_valor())

# Mostrar número de passos por episódio
print(f"\nPassos por episódio: {num_passos_episodio}")