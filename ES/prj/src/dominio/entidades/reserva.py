class Reserva:
    """Classe Reserva

    Representa o conceito de Reserva no contexto do projeto
    """

    def __init__(self):
        self._id_reserva = None
        self._data_criacao = None
        self._data_entrada_prev = None
        self._data_saida_prev = None
        self._estado = None
        self._valor_total_prev = None
        self._notas = None

    # GETS E SETS

    def get_id_reserva(self):
        return self._id_reserva

    def set_id_reserva(self, id_reserva):
        self._id_reserva = id_reserva

    def get_data_criacao(self):
        return self._data_criacao

    def set_data_criacao(self, data_criacao):
        self._data_criacao = data_criacao

    def get_data_entrada_prev(self):
        return self._data_entrada_prev

    def set_data_entrada_prev(self, data_entrada_prev):
        self._data_entrada_prev = data_entrada_prev

    def get_data_saida_prev(self):
        return self._data_saida_prev

    def set_data_saida_prev(self, data_saida_prev):
        self._data_saida_prev = data_saida_prev

    def get_estado(self):
        return self._estado

    def set_estado(self, estado):
        self._estado = estado

    def get_valor_total_prev(self):
        return self._valor_total_prev

    def set_valor_total_prev(self, valor_total_prev):
        self._valor_total_prev = valor_total_prev

    def get_notas(self):
        return self._notas

    def set_notas(self, notas):
        self._notas = notas