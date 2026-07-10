class Rotas:
    def __init__(self, servico_hospede):
        self.servico_hospede = servico_hospede
    
    def registar_hospede(self, dados_hospede):
        """Rota para registar um novo hóspede"""
        try:
            # Validar dados obrigatórios
            campos_obrigatorios = ['nomeCompleto', 'numDocumento', 'validadeDoc', 
                                  'birthDate', 'nacionalidade', 'email', 'telemovel']
            
            for campo in campos_obrigatorios:
                if campo not in dados_hospede or not dados_hospede[campo]:
                    return {
                        'success': False,
                        'message': f'Campo obrigatório faltando: {campo}'
                    }, 400
            
            # serviço para registar hóspede
            resultado = self.servico_hospede.registar_hospede(dados_hospede)
            
            return resultado
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro interno do servidor: {str(e)}'
            }, 500
    
    def consultar_hospede(self, email):
        """Rota para consultar hóspede por email"""
        try:
            if not email:
                return {
                    'success': False,
                    'message': 'Email é obrigatório'
                }, 400
            
            # serviço para consultar hóspede
            resultado = self.servico_hospede.consulta_hospede(email)
            
            return resultado
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro interno do servidor: {str(e)}'
            }, 500