import mysql.connector

class RepositorioQuartoSQL:

    def __init__(self):
        # Configuração da conexão com o MySQL
        self.connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='hotel'
        )
        self.cursor = self.connection.cursor(dictionary=True)
    
    def listar_disponiveis(self):
        try:
            # Query para listar quartos disponíveis
            query = """
            SELECT q.numero, q.tipo, q.precoBase, q.estadoAtual
            FROM quarto q
            WHERE q.estadoAtual = 'DISPONIVEL'
            ORDER BY q.numero
            """
            
            self.cursor.execute(query)
            quartos = self.cursor.fetchall()
            return quartos
            
        except mysql.connector.Error as err:
            print(f"Erro ao listar quartos disponíveis: {err}")
            return []
    
    def listar_por_tipo(self, tipo_quarto):
        """Lista quartos por tipo"""
        try:
            query = """
            SELECT q.numero, q.tipo, q.precoBase, q.estadoAtual
            FROM quarto q
            WHERE q.tipo = %s AND q.estadoAtual = 'DISPONIVEL'
            ORDER BY q.numero
            """
            
            self.cursor.execute(query, (tipo_quarto,))
            quartos = self.cursor.fetchall()
            return quartos
            
        except mysql.connector.Error as err:
            print(f"Erro ao listar quartos por tipo: {err}")
            return []
    
    def obter_quarto(self, numero_quarto):
        """Obtém informações de um quarto específico"""
        try:
            query = """
            SELECT q.numero, q.tipo, q.precoBase, q.estadoAtual
            FROM quarto q
            WHERE q.numero = %s
            """
            
            self.cursor.execute(query, (numero_quarto,))
            quarto = self.cursor.fetchone()
            return quarto
            
        except mysql.connector.Error as err:
            print(f"Erro ao obter quarto: {err}")
            return None
    
    def atualizar_estado(self, numero_quarto, novo_estado):
        """Atualiza o estado de um quarto"""
        try:
            query = """
            UPDATE quarto 
            SET estadoAtual = %s
            WHERE numero = %s
            """
            
            self.cursor.execute(query, (novo_estado, numero_quarto))
            self.connection.commit()
            return True
            
        except mysql.connector.Error as err:
            print(f"Erro ao atualizar estado do quarto: {err}")
            return False
    
    def listar_ativos(self):
        """Lista todos os quartos ativos"""
        try:
            query = """
            SELECT q.numero, q.tipo, q.precoBase, q.estadoAtual
            FROM quarto q
            WHERE q.estadoAtual != 'INATIVO'
            ORDER BY q.numero
            """
            
            self.cursor.execute(query)
            quartos = self.cursor.fetchall()
            return quartos
            
        except mysql.connector.Error as err:
            print(f"Erro ao listar quartos ativos: {err}")
            return []
    
    def criar(self, quarto):
        """Cria um novo quarto"""
        try:
            query = """
            INSERT INTO quarto (numero, tipo, precoBase, estadoAtual)
            VALUES (%s, %s, %s, %s)
            """
            
            valores = (
                quarto['numero'],
                quarto['tipo'],
                quarto['precoBase'],
                quarto.get('estadoAtual', 'DISPONIVEL')
            )
            
            self.cursor.execute(query, valores)
            self.connection.commit()
            return self.cursor.lastrowid
            
        except mysql.connector.Error as err:
            print(f"Erro ao criar quarto: {err}")
            raise
    
    def eliminar(self, numero):
        """Elimina um quarto"""
        try:
            query = "DELETE FROM quarto WHERE numero = %s"
            self.cursor.execute(query, (numero,))
            self.connection.commit()
            return self.cursor.rowcount > 0
            
        except mysql.connector.Error as err:
            print(f"Erro ao eliminar quarto: {err}")
            raise