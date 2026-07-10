from dominio.servicos.servico_hospede import ServicoHospede


def teste_registo():
    """Função para teste"""
    print("=== TESTE DE REGISTO DE HÓSPEDE ===")
    
    servico = ServicoHospede()
    
    # Documento único baseado no timestamp para evitar conflitos nos testes
    import time
    timestamp = int(time.time())
    num_doc = f"TESTE{timestamp}"
    email = f"teste{timestamp}@email.com"
    
    dados_hospede = {
        'nomeCompleto': 'Teste Automático',
        'numDocumento': num_doc,
        'validadeDoc': '2025-12-31',
        'birthDate': '1995-01-01',
        'nacionalidade': 'pt',
        'email': email,  
        'telemovel': '911111111',
        'preferencias': 'Teste automático do sistema'
    }
    
    print(f"\nTentando registar hóspede com documento: {num_doc}")
    print(f"Email: {email}")
    
    resultado = servico.registar_hospede(dados_hospede)
    
    if resultado.get('success'):
        print(f"\nSUCESSO!")
        print(f"   Mensagem: {resultado.get('message')}")
        print(f"   ID do hóspede: {resultado.get('idHospede')}")
    else:
        print(f"\nFALHA!")
        print(f"   Mensagem: {resultado.get('message')}")
    
    return resultado

if __name__ == '__main__':
    teste_registo()