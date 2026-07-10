from acesso_dados.repositorio_consumo_sql import RepositorioConsumoSQL

class TesteListarConsumos:
    def __init__(self):
        self.repositorio = RepositorioConsumoSQL()
    
    def testar_listar_servicos_disponiveis(self):
        """
        Testa a função de listar consumos/serviços
        """
        print(f"\n{'='*50}")
        print(f"Teste: Listar Serviços")
        print(f"{'='*50}")
        
        try:
            # Chama a função do repositório
            servicos = self.repositorio.listar_consumos()

            print(servicos)

            if servicos:
                print(f"\nEncontrados {len(servicos)} disponíveeis:")
                print(f"{'-'*50}")
                
                for i, servico in enumerate(servicos, 1):
                    print(f"Serviço #{i}:")
                    print(f"  ID: {servico['idServico']}")
                    print(f"  Nome: {servico['nomeServico']}")
                    print(f"  Preço: €{servico['preco']:.2f}")
                    
            else:
                print(f"Nenhum quarto disponível encontrado.")
                
            return servicos
            
        except Exception as e:
            print(f"\nErro ao listar quartos disponíveis: {e}")
            import traceback
            traceback.print_exc()
            return None

if __name__ == "__main__":
    tester = TesteListarConsumos()
    tester.testar_listar_servicos_disponiveis()