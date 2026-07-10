import mysql.connector

class RepositorioConsumoSQL:

    def __init__(self):
        # Configuração da conexão com o MySQL
        self.connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='hotel'
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def listar_consumos(self):
        try:
            # Query para listar quartos disponíveis
            query = """
            SELECT *
            FROM servico
            """
            
            self.cursor.execute(query)
            servicos = self.cursor.fetchall()
            return servicos
            
        except mysql.connector.Error as err:
            print(f"Erro ao listar quartos disponíveis: {err}")
            return []
    
    def criar(self, servico):
        raise NotImplementedError
    
    def eliminar(self, servico):
        raise NotImplementedError