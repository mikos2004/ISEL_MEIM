from acesso_dados.repositorio_quarto_sql import RepositorioQuartoSQL

class TesteListarQuartosDisp:
    def __init__(self):
        self.repositorio = RepositorioQuartoSQL()
    
    def testar_listar_quartos_disponiveis(self):
        """
        Testa a função de listar quartos disponíveis
        """
        print(f"\n{'='*50}")
        print(f"Teste: Listar Quartos Disponíveis")
        print(f"{'='*50}")
        
        try:
            # Chama a função do repositório
            quartos_disponiveis = self.repositorio.listar_disponiveis()

            #print(quartos_disponiveis)

            if quartos_disponiveis:
                print(f"\nEncontrados {len(quartos_disponiveis)} quartos disponíveis:")
                print(f"{'-'*50}")
                
                for i, quarto in enumerate(quartos_disponiveis, 1):
                    print(f"\nQuarto #{i}:")
                    print(f"  Número: {quarto['numero']}")
                    print(f"  Tipo: {quarto['tipo']}")
                    print(f"  Preço por noite: €{quarto['precoBase']:.2f}")
                    
            else:
                print(f"Nenhum quarto disponível encontrado.")
                
            return quartos_disponiveis
            
        except Exception as e:
            print(f"\nErro ao listar quartos disponíveis: {e}")
            import traceback
            traceback.print_exc()
            return None

if __name__ == "__main__":
    tester = TesteListarQuartosDisp()
    tester.testar_listar_quartos_disponiveis()