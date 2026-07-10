class DadosReserva:

    def __init__(self):
        self._id_reserva = None
        self._data_criacao = None
        self._data_entrada_prev = None
        self._data_saida_prev = None
        self._estado = None
        self._valor_total_prev = None
        self._notas = None
    
    # Getters (sem setters, porque é read_only como indicado nos diagramas)

    def get_id_reserva(self):
        return self._id_reserva

    def get_data_criacao(self):
        return self._data_criacao

    def get_data_entrada_prev(self):
        return self._data_entrada_prev

    def get_data_saida_prev(self):
        return self._data_saida_prev

    def get_estado(self):
        return self._estado

    def get_valor_total_prev(self):
        return self._valor_total_prev

    def get_notas(self):
        return self._notas