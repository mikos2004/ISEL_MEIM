class Hospede:
    def __init__(self):
        self.nome_completo = ""
        self.num_documento = ""
        self.validade_doc = None
        self.birth_date = None
        self.nacionalidade = ""
        self.email = ""
        self.telemovel = ""
        self.morada = ""
        self.preferencias = ""
        self.historico = []

    def get_nome_completo(self):
        return self.nome_completo

    def set_nome_completo(self, nome_completo):
        self.nome_completo = nome_completo

    def get_num_documento(self):
        return self.num_documento

    def set_num_documento(self, num_documento):
        self.num_documento = num_documento

    def get_validade_doc(self):
        return self.validade_doc

    def set_validade_doc(self, validade_doc):
        self.validade_doc = validade_doc

    def get_birth_date(self):
        return self.birth_date

    def set_birth_date(self, birth_date):
        self.birth_date = birth_date

    def get_nacionalidade(self):
        return self.nacionalidade

    def set_nacionalidade(self, nacionalidade):
        self.nacionalidade = nacionalidade

    def get_email(self):
        return self.email

    def set_email(self, email):
        self.email = email

    def get_telemovel(self):
        return self.telemovel

    def set_telemovel(self, telemovel):
        self.telemovel = telemovel

    def get_morada(self):
        return self.morada

    def set_morada(self, morada):
        self.morada = morada

    def get_preferencias(self):
        return self.preferencias

    def set_preferencias(self, preferencias):
        self.preferencias = preferencias

    def get_historico(self):
        return self.historico

    def set_historico(self, historico):
        self.historico = historico