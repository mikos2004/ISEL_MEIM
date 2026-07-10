class DadosHospedes:

    def __init__(self):
        self._nome_completo = None
        self._num_documento = None
        self._validade_doc = None
        self._birth_date = None
        self._nacionalidade = None
        self._email = None
        self._telemovel = None
        self._morada = None
        self._preferencias = None
        self._historico = []  # Inicializa com lista vazia

    # Getters (sem setters, porque é read_only como indicado nos diagramas)
    
    def get_nome_completo(self):
        return self._nome_completo

    def get_num_documento(self):
        return self._num_documento

    def get_validade_doc(self):
        return self._validade_doc

    def get_birth_date(self):
        return self._birth_date

    def get_nacionalidade(self):
        return self._nacionalidade

    def get_email(self):
        return self._email

    def get_telemovel(self):
        return self._telemovel

    def get_morada(self):
        return self._morada

    def get_preferencias(self):
        return self._preferencias

    def get_historico(self):
        return self._historico