from acesso_dados.repositorio_hospede_sql import RepositorioHospedeSQL


class ServicoHospede:
    def __init__(self):
        self.rep_hosp = RepositorioHospedeSQL()

    def consulta_hospede(self, mail):
        """Consulta hóspede por email"""
        try:
            hospede = self.rep_hosp.obter_hospede_por_email(mail)
            if hospede:
                return {
                    'success': True,
                    'hospede': hospede
                }
            else:
                return {
                    'success': False,
                    'message': 'Hóspede não encontrado'
                }, 404
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao consultar hóspede: {str(e)}'
            }, 500

    def registar_doc(self, num_doc):
        """Regista documento do hóspede"""
        try:
            existe = self.rep_hosp.verificar_documento(num_doc)
            return {
                'success': True,
                'existe': existe
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao verificar documento: {str(e)}'
            }, 500

    def carregar_hospede(self):
        """Carrega dados do hóspede"""
        # Implementação depende do contexto
        pass

    def registar_hospede(self, dados_hospede):
        """Regista novo hóspede"""
        try:
            # Verificar se documento já existe
            existe = self.rep_hosp.verificar_documento(dados_hospede['numDocumento'])
            
            if existe:
                return {
                    'success': False,
                    'message': 'Documento já está registado'
                }, 409  # Conflict
            
            # Registar hóspede
            resultado = self.rep_hosp.registar(dados_hospede)
            
            return resultado
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao registar hóspede: {str(e)}'
            }, 500