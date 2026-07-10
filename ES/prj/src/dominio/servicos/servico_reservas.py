import datetime
from acesso_dados.repositorio_quarto_sql import RepositorioQuartoSQL
from acesso_dados.repositorio_reserva_sql import RepositorioReservaSQL
from acesso_dados.repositorio_consumo_sql import RepositorioConsumoSQL


class ServicoReservas:

    def __init__(self):
        self.rep_quartos = RepositorioQuartoSQL()
        self.rep_reservas = RepositorioReservaSQL()
        self.rep_consumos = RepositorioConsumoSQL()
        self.precos_servicos = self._carregar_precos_servicos()

    def _carregar_precos_servicos(self):
        """Carrega os preços dos serviços do banco de dados"""
        try:
            servicos_db = self.rep_consumos.listar_consumos()
            precos = {}
            for servico in servicos_db:
                precos[servico['nomeServico']] = float(servico['preco'])
            return precos
        except Exception as e:
            return "Erro ao carregar preços dos serviços"
            
        
    def atualizar_precos_servicos(self):
        """Atualiza os preços dos serviços do banco de dados"""
        self.precos_servicos = self._carregar_precos_servicos()
        return self.precos_servicos
        
    def check_disp_quartos(self, tipo_quarto=None):
        """Verifica disponibilidade de quartos"""
        try:
            if tipo_quarto:
                return self.rep_quartos.listar_por_tipo(tipo_quarto)
            else:
                return self.rep_quartos.listar_disponiveis()
        except Exception as e:
            print(f"Erro ao verificar disponibilidade: {e}")
            return []
        
    def calc_valor_total_reserva(self, dados_reserva):
        """Calcula valor total da reserva"""
        try:
            # Obter informações do quarto
            if dados_reserva.get('numeroQuarto'):
                quarto = self.rep_quartos.obter_quarto(dados_reserva['numeroQuarto'])
            else:
                # Se não especificar número, assume o primeiro disponível do tipo
                quartos_tipo = self.rep_quartos.listar_por_tipo(dados_reserva['tipoQuarto'])
                if not quartos_tipo:
                    raise ValueError(f"Não há quartos disponíveis do tipo {dados_reserva['tipoQuarto']}")
                quarto = quartos_tipo[0]
                dados_reserva['numeroQuarto'] = quarto['numero']
            
            if not quarto:
                raise ValueError(f"Quarto não encontrado: {dados_reserva.get('numeroQuarto')}")
            
            # Calcular número de dias
            data_entrada = datetime.datetime.strptime(dados_reserva['dataEntradaPrev'], '%Y-%m-%d').date()
            data_saida = datetime.datetime.strptime(dados_reserva['dataSaidaPrev'], '%Y-%m-%d').date()
            numero_dias = (data_saida - data_entrada).days
            
            if numero_dias <= 0:
                raise ValueError("Número de dias deve ser positivo")
            
            # Calcular valor base
            valor_base = quarto['precoBase'] * numero_dias
            
            # Adicionar serviços adicionais
            valor_servicos = 0
            if dados_reserva.get('servicosAdicionais'):
                servico = dados_reserva['servicosAdicionais']
                if servico in self.precos_servicos:
                    valor_servicos = self.precos_servicos[servico] * numero_dias
                else:
                    # Tenta encontrar por nome aproximado (case-insensitive)
                    servico_lower = servico.lower()
                    for nome_servico, preco in self.precos_servicos.items():
                        if servico_lower in nome_servico.lower() or nome_servico.lower() in servico_lower:
                            valor_servicos = preco * numero_dias
                            break
            
            # Calcular total
            valor_total = valor_base + valor_servicos
            
            return {
                'valorBase': valor_base,
                'valorServicos': valor_servicos,
                'valorTotal': valor_total,
                'numeroDias': numero_dias,
                'quarto': quarto
            }
            
        except Exception as e:
            print(f"Erro ao calcular valor total: {e}")
            raise

    def criar_reserva(self, dados_reserva):
        """Cria uma nova reserva"""
        try:
            # Verificar disponibilidade do quarto
            if not self.rep_reservas.verificar_disponibilidade(
                dados_reserva['numeroQuarto'],
                dados_reserva['dataEntradaPrev'],
                dados_reserva['dataSaidaPrev']
            ):
                raise ValueError(f"Quarto {dados_reserva['numeroQuarto']} não está disponível para as datas selecionadas")
            
            # Calcular valor total
            calculo_valor = self.calc_valor_total_reserva(dados_reserva)
            
            # Preparar dados para a reserva
            reserva_data = {
                'dataEntradaPrev': dados_reserva['dataEntradaPrev'],
                'dataSaidaPrev': dados_reserva['dataSaidaPrev'],
                'estado': 'CONFIRMADA',
                'valorTotalPrev': calculo_valor['valorTotal'],
                'notas': dados_reserva.get('notas', ''),
                'idHospede': dados_reserva['idHospede'],
                'numeroQuarto': dados_reserva['numeroQuarto']
            }
            
            # Criar reserva no banco de dados
            id_reserva = self.rep_reservas.criar(reserva_data)
            
            if id_reserva:
                # Atualizar estado do quarto para RESERVADO
                self.rep_quartos.atualizar_estado(
                    dados_reserva['numeroQuarto'], 
                    'RESERVADO'
                )
                
                return {
                    'idReserva': id_reserva,
                    'valorTotalPrev': calculo_valor['valorTotal'],
                    'numeroDias': calculo_valor['numeroDias'],
                    'numeroQuarto': dados_reserva['numeroQuarto'],
                    'tipoQuarto': calculo_valor['quarto']['tipo'],
                    'precosServicos': self.precos_servicos
                }
            else:
                raise ValueError("Erro ao criar reserva no banco de dados")
                
        except Exception as e:
            print(f"Erro ao criar reserva: {e}")
            raise

    def get_lista_hosp_ativos(self):
        # Obtém lista de hóspedes ativos
        raise NotImplementedError

    def calcular_total_conta(self):
        # Calcula total da conta
        raise NotImplementedError

    def ajustar_datas(self):
        # Ajusta datas da reserva
        raise NotImplementedError

    def adicionar_consumos(self):
        # Adiciona consumos à reserva depois da criação
        raise NotImplementedError

    def atualizar_conta(self):
        # Atualiza conta da reserva
        raise NotImplementedError

    def obter_lista_reserva(self):
        # Obtém lista de reservas
        raise NotImplementedError

    def get_disponibilidade(self):
        # Obtém disponibilidade
        raise NotImplementedError