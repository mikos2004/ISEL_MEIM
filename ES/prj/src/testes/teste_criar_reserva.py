from dominio.servicos.servico_reservas import ServicoReservas
from dominio.servicos.servico_hospede import ServicoHospede
import time

def teste_criar_reserva():
    """Função para teste de criação de reserva"""
    print("=== TESTE DE CRIAÇÃO DE RESERVA ===")
    
    # Inicializar serviços
    servico_hospede = ServicoHospede()
    servico_reservas = ServicoReservas()
    
    # 1. Primeiro, criar um hóspede de teste
    print("\n--- Criando hóspede de teste ---")
    timestamp = int(time.time())
    num_doc = f"TESTERES{timestamp}"
    email = f"teste.reserva{timestamp}@email.com"
    
    dados_hospede = {
        'nomeCompleto': 'Teste Reserva Automática',
        'numDocumento': num_doc,
        'validadeDoc': '2025-12-31',
        'birthDate': '1990-05-15',
        'nacionalidade': 'pt',
        'email': email,
        'telemovel': '912345678',
        'preferencias': 'Teste automático de reserva'
    }
    
    print(f"Registando hóspede com documento: {num_doc}")
    print(f"Email: {email}")
    
    resultado_hospede = servico_hospede.registar_hospede(dados_hospede)
    
    if not resultado_hospede.get('success'):
        print(f"FALHA ao criar hóspede: {resultado_hospede.get('message')}")
        return resultado_hospede
    
    id_hospede = resultado_hospede.get('idHospede')
    print(f"SUCESSO! ID do hóspede: {id_hospede}")
    
    # 2. Verificar quartos disponíveis
    print("\n--- Verificando quartos disponíveis ---")
    quartos_disponiveis = servico_reservas.check_disp_quartos()
    
    if not quartos_disponiveis:
        print("Nenhum quarto disponível para teste!")
        return {
            'success': False,
            'message': 'Nenhum quarto disponível'
        }
    
    # Usar o primeiro quarto disponível
    quarto_selecionado = quartos_disponiveis[0]
    print(f"Quarto selecionado: {quarto_selecionado['numero']} - {quarto_selecionado['tipo']}")
    print(f"Preço base: {quarto_selecionado['precoBase']}€/noite")
    
    # 3. Preparar dados da reserva
    print("\n--- Preparando dados da reserva ---")
    
    # Datas de teste (amanhã para 3 dias depois)
    from datetime import datetime, timedelta
    hoje = datetime.now()
    entrada = (hoje + timedelta(days=1)).strftime('%Y-%m-%d')
    saida = (hoje + timedelta(days=4)).strftime('%Y-%m-%d')
    
    dados_reserva = {
        'idHospede': id_hospede,
        'numeroQuarto': quarto_selecionado['numero'],
        'tipoQuarto': quarto_selecionado['tipo'],
        'dataEntradaPrev': entrada,
        'dataSaidaPrev': saida,
        'servicosAdicionais': 'Café da Manhã',  # Serviço opcional
        'notas': 'Reserva criada por teste automático'
    }
    
    print(f"Data de entrada: {entrada}")
    print(f"Data de saída: {saida}")
    print(f"Duração: 3 noites")
    print(f"Serviço adicional: {dados_reserva['servicosAdicionais']}")
    
    # 4. Calcular valor total (opcional, para verificação)
    print("\n--- Calculando valor total ---")
    try:
        calculo = servico_reservas.calc_valor_total_reserva(dados_reserva)
        print(f"Valor base: {calculo['valorBase']}€")
        print(f"Valor serviços: {calculo['valorServicos']}€")
        print(f"VALOR TOTAL: {calculo['valorTotal']}€")
        print(f"Número de dias: {calculo['numeroDias']}")
    except Exception as e:
        print(f"Erro no cálculo: {e}")
    
    # 5. Criar a reserva
    print("\n--- Criando reserva ---")
    
    try:
        resultado_reserva = servico_reservas.criar_reserva(dados_reserva)
        
        print(f"\nSUCESSO!")
        print(f"   ID da reserva: {resultado_reserva.get('idReserva')}")
        print(f"   Valor total: {resultado_reserva.get('valorTotalPrev')}€")
        print(f"   Número de dias: {resultado_reserva.get('numeroDias')}")
        print(f"   Quarto: {resultado_reserva.get('numeroQuarto')}")
        print(f"   Tipo de quarto: {resultado_reserva.get('tipoQuarto')}")
        print(f"   Mensagem: Reserva criada com sucesso!")
        
        # 6. Verificar se o quarto foi atualizado para RESERVADO
        print("\n--- Verificando estado do quarto ---")
        quarto_atual = servico_reservas.rep_quartos.obter_quarto(quarto_selecionado['numero'])
        print(f"   Estado atual do quarto: {quarto_atual.get('estadoAtual')}")
        
        return {
            'success': True,
            'idHospede': id_hospede,
            'reserva': resultado_reserva,
            'message': 'Reserva criada com sucesso'
        }
        
    except ValueError as e:
        print(f"\nFALHA - Erro de validação!")
        print(f"   Mensagem: {str(e)}")
        return {
            'success': False,
            'message': str(e),
            'tipo': 'validacao'
        }
    except Exception as e:
        print(f"\nFALHA - Erro geral!")
        print(f"   Mensagem: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'message': str(e),
            'tipo': 'geral'
        }


if __name__ == '__main__':
    resultado = teste_criar_reserva()
    
    print("\n" + "="*50)
    print("RESUMO DO TESTE:")
    print(f"Status: {'SUCESSO' if resultado.get('success') else 'FALHA'}")
    if resultado.get('success'):
        print(f"ID Hóspede: {resultado.get('idHospede')}")
        print(f"ID Reserva: {resultado.get('reserva', {}).get('idReserva')}")
    else:
        print(f"Mensagem de erro: {resultado.get('message')}")