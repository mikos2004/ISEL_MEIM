import mysql.connector
from datetime import datetime

class RepositorioHospedeSQL:
    def __init__(self):
        # Configuração da conexão com o MySQL
        self.connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='hotel'
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def obter_hospede(self, num_doc):
        """Obtém hóspede por número de documento"""
        try:
            query = "SELECT * FROM hospede WHERE numDocumento = %s"
            self.cursor.execute(query, (num_doc,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Erro ao obter hóspede: {e}")
            raise

    def obter_hospede_por_email(self, email):
        """Obtém hóspede por email (método novo)"""
        try:
            query = "SELECT * FROM hospede WHERE email = %s"
            self.cursor.execute(query, (email,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Erro ao obter hóspede por email: {e}")
            raise

    def verificar_documento(self, num_doc):
        """Verifica se documento já existe"""
        try:
            query = "SELECT COUNT(*) as count FROM hospede WHERE numDocumento = %s"
            self.cursor.execute(query, (num_doc,))
            result = self.cursor.fetchone()
            return result['count'] > 0
        except Exception as e:
            print(f"Erro ao verificar documento: {e}")
            raise

    def registar(self, hospede):
        """Regista um novo hóspede"""
        try:
            query = """
            INSERT INTO hospede 
            (nomeCompleto, numDocumento, validadeDoc, birthDate, 
             nacionalidade, email, telemovel, preferencias) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            valores = (
                hospede['nomeCompleto'],
                hospede['numDocumento'],
                hospede['validadeDoc'],
                hospede['birthDate'],
                hospede['nacionalidade'],
                hospede['email'],
                hospede['telemovel'],
                hospede.get('preferencias', '')
            )
            
            self.cursor.execute(query, valores)
            self.connection.commit()
            
            # Obter o ID do hóspede inserido
            id_hospede = self.cursor.lastrowid
            
            return {
                'success': True,
                'message': 'Hóspede registado com sucesso',
                'idHospede': id_hospede
            }
            
        except mysql.connector.Error as err:
            # Se for erro de duplicação
            if err.errno == 1062:  # ER_DUP_ENTRY
                return {
                    'success': False,
                    'message': 'Documento ou email já está registado'
                }
            else:
                print(f"Erro MySQL ao registar: {err}")
                return {
                    'success': False,
                    'message': f'Erro de banco de dados: {err}'
                }
        except Exception as e:
            print(f"Erro ao registar hóspede: {e}")
            return {
                'success': False,
                'message': f'Erro interno: {str(e)}'
            }
    
    def eliminar(self, num_doc):
        """Elimina um hóspede pelo número de documento"""
        try:
            query = "DELETE FROM hospede WHERE numDocumento = %s"
            self.cursor.execute(query, (num_doc,))
            self.connection.commit()
            
            return self.cursor.rowcount > 0
            
        except Exception as e:
            print(f"Erro ao eliminar hóspede: {e}")
            raise