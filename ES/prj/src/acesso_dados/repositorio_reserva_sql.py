import mysql.connector
from datetime import datetime

class RepositorioReservaSQL:
    
    def __init__(self):
        # Configuração da conexão com o MySQL
        self.connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='hotel'
        )
        self.cursor = self.connection.cursor(dictionary=True)
    
    def verificar_disponibilidade(self, numero_quarto, data_entrada, data_saida):
        """Verifica se o quarto está disponível para as datas solicitadas"""
        try:
            query = """
            SELECT COUNT(*) as count
            FROM reserva r
            WHERE r.numeroQuarto = %s
            AND r.estado NOT IN ('CANCELADA', 'FINALIZADA')
            AND (
                (%s BETWEEN r.dataEntradaPrev AND DATE_SUB(r.dataSaidaPrev, INTERVAL 1 DAY))
                OR (%s BETWEEN DATE_ADD(r.dataEntradaPrev, INTERVAL 1 DAY) AND r.dataSaidaPrev)
                OR (r.dataEntradaPrev BETWEEN %s AND DATE_SUB(%s, INTERVAL 1 DAY))
            )
            """
            
            self.cursor.execute(query, (
                numero_quarto,
                data_entrada,
                data_saida,
                data_entrada,
                data_saida
            ))
            
            result = self.cursor.fetchone()
            return result['count'] == 0  # Disponível se count = 0
            
        except mysql.connector.Error as err:
            print(f"Erro ao verificar disponibilidade: {err}")
            return False
    
    def criar(self, reserva):
        """Cria uma nova reserva"""
        try:
            query = """
            INSERT INTO reserva 
            (dataEntradaPrev, dataSaidaPrev, estado, valorTotalPrev, 
             notas, idHospede, numeroQuarto, dataCriacao)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            valores = (
                reserva['dataEntradaPrev'],
                reserva['dataSaidaPrev'],
                reserva['estado'],
                reserva['valorTotalPrev'],
                reserva['notas'],
                reserva['idHospede'],
                reserva['numeroQuarto'],
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            self.cursor.execute(query, valores)
            self.connection.commit()
            
            return self.cursor.lastrowid
            
        except mysql.connector.Error as err:
            print(f"Erro ao criar reserva: {err}")
            raise
    
    def obter_lista(self):
        """Obtém lista de todas as reservas"""
        try:
            query = """
            SELECT r.*, h.nomeCompleto as nomeHospede, q.tipo as tipoQuarto
            FROM reserva r
            JOIN hospede h ON r.idHospede = h.idHospede
            JOIN quarto q ON r.numeroQuarto = q.numero
            ORDER BY r.dataCriacao DESC
            """
            
            self.cursor.execute(query)
            reservas = self.cursor.fetchall()
            return reservas
            
        except mysql.connector.Error as err:
            print(f"Erro ao obter lista de reservas: {err}")
            return []
    
    def obter(self, id_reserva):
        """Obtém uma reserva específica"""
        try:
            query = """
            SELECT r.*, h.nomeCompleto as nomeHospede, q.tipo as tipoQuarto
            FROM reserva r
            JOIN hospede h ON r.idHospede = h.idHospede
            JOIN quarto q ON r.numeroQuarto = q.numero
            WHERE r.idReserva = %s
            """
            
            self.cursor.execute(query, (id_reserva,))
            reserva = self.cursor.fetchone()
            return reserva
            
        except mysql.connector.Error as err:
            print(f"Erro ao obter reserva: {err}")
            return None
    
    def atualizar_estado(self, id_reserva, novo_estado):
        """Atualiza o estado de uma reserva"""
        try:
            query = """
            UPDATE reserva 
            SET estado = %s
            WHERE idReserva = %s
            """
            
            self.cursor.execute(query, (novo_estado, id_reserva))
            self.connection.commit()
            return self.cursor.rowcount > 0
            
        except mysql.connector.Error as err:
            print(f"Erro ao atualizar estado da reserva: {err}")
            return False
    
    def obter_por_hospede(self, id_hospede):
        """Obtém reservas de um hóspede específico"""
        try:
            query = """
            SELECT r.*, q.tipo as tipoQuarto
            FROM reserva r
            JOIN quarto q ON r.numeroQuarto = q.numero
            WHERE r.idHospede = %s
            ORDER BY r.dataCriacao DESC
            """
            
            self.cursor.execute(query, (id_hospede,))
            reservas = self.cursor.fetchall()
            return reservas
            
        except mysql.connector.Error as err:
            print(f"Erro ao obter reservas do hóspede: {err}")
            return []