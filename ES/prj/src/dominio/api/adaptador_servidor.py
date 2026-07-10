from flask import Flask, request, jsonify
from flask_cors import CORS

from acesso_dados.repositorio_hospede_sql import RepositorioHospedeSQL
from dominio.api.rotas import Rotas
from dominio.servicos.servico_hospede import ServicoHospede
from dominio.servicos.servico_reservas import ServicoReservas


app = Flask(__name__)
CORS(app)

# repositório e serviço
rep_hosp = RepositorioHospedeSQL()
servico_hospede = ServicoHospede()
servico_reservas = ServicoReservas()

# Instanciar rotas
rotas = Rotas(servico_hospede)

@app.route('/api/registar_hosp', methods=['POST'])
def registar_hosp():
    """Endpoint para registar hóspede"""
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({
                'success': False,
                'message': 'Nenhum dado fornecido'
            }), 400
        
        resultado = rotas.registar_hospede(dados)
        
        if isinstance(resultado, tuple) and len(resultado) == 2:
            return jsonify(resultado[0]), resultado[1]
        else:
            return jsonify(resultado)
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro no servidor: {str(e)}'
        }), 500

@app.route('/api/consulta_hospede', methods=['GET'])
def consulta_hospede():
    """Endpoint para consultar hóspede por email"""
    try:
        email = request.args.get('email')
        
        if not email:
            return jsonify({
                'success': False,
                'message': 'Parâmetro email é obrigatório'
            }), 400
        
        resultado = rotas.consultar_hospede(email)
        
        if isinstance(resultado, tuple) and len(resultado) == 2:
            return jsonify(resultado[0]), resultado[1]
        else:
            return jsonify(resultado)
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro no servidor: {str(e)}'
        }), 500


@app.route('/api/confirm_reserva', methods=['POST'])
def confirm_reserva():
	try:
		dados = request.get_json()
		
		# Validar dados obrigatórios
		campos_obrigatorios = [
			'idHospede', 'dataEntradaPrev', 'dataSaidaPrev'
		]
		
		for campo in campos_obrigatorios:
			if campo not in dados or not dados[campo]:
				return jsonify({
					'success': False,
					'message': f'Campo obrigatório ausente: {campo}'
				}), 400
		
		# Se não especificar número do quarto, mas especificar tipo
		if not dados.get('numeroQuarto') and dados.get('tipoQuarto'):
			# procurar quarto disponível do tipo especificado
			quartos_disponiveis = servico_reservas.check_disp_quartos(dados['tipoQuarto'])
			if not quartos_disponiveis:
				return jsonify({
					'success': False,
					'message': f'Não há quartos disponíveis do tipo {dados["tipoQuarto"]}'
				}), 400
			
			# usa primeiro quarto disponível
			dados['numeroQuarto'] = quartos_disponiveis[0]['numero']
		elif dados.get('numeroQuarto'):
			# Verifica se o quarto específico está disponível
			quarto = servico_reservas.rep_quartos.obter_quarto(dados['numeroQuarto'])
			if not quarto:
				return jsonify({
					'success': False,
					'message': f'Quarto {dados["numeroQuarto"]} não encontrado'
				}), 400
			
			if quarto['estadoAtual'] != 'DISPONIVEL':
				return jsonify({
					'success': False,
					'message': f'Quarto {dados["numeroQuarto"]} não está disponível'
				}), 400
		
		# Criar reserva
		resultado = servico_reservas.criar_reserva(dados)
		
		return jsonify({
			'success': True,
			'idReserva': resultado['idReserva'],
			'valorTotalPrev': resultado['valorTotalPrev'],
			'numeroDias': resultado['numeroDias'],
			'numeroQuarto': resultado['numeroQuarto'],
			'tipoQuarto': resultado['tipoQuarto'],
			'message': 'Reserva confirmada com sucesso'
		})
		
	except ValueError as e:
		return jsonify({
			'success': False,
			'message': str(e)
		}), 400
	except Exception as e:
		return jsonify({
			'success': False,
			'message': f'Erro interno: {str(e)}'
		}), 500

@app.route('/api/quartos_disponiveis', methods=['GET'])
def quartos_disponiveis():
	try:
		tipo = request.args.get('tipo')
		if tipo:
			quartos = servico_reservas.check_disp_quartos(tipo)
		else:
			quartos = servico_reservas.check_disp_quartos()
		
		return jsonify(quartos)
		
	except Exception as e:
		return jsonify({
			'success': False,
			'message': f'Erro ao obter quartos disponíveis: {str(e)}'
		}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5008)