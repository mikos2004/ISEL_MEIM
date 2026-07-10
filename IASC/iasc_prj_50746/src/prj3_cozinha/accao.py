from enum import Enum

"""
Lista de ações que o agente pode selecionar no problema da cozinha
"""
class AccaoCozinha(Enum):
    INICIAR_AGUA = 0
    INICIAR_MASSA = 1
    ESPERAR = 2
    FINALIZAR = 3