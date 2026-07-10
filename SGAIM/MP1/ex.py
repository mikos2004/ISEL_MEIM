def analisar_nomes(ficheiro="input.txt"):
    """
    Lê um ficheiro com nomes e calcula:
    - Comprimento do nome mais pequeno
    - Média do comprimento dos nomes
    - Comprimento do nome mais longo
    """
    try:
        # Abrir e ler o ficheiro
        with open(ficheiro, 'r', encoding='utf-8') as f:
            # Ler todas as linhas, remover espaços em branco e ignorar linhas vazias
            nomes = [linha.strip() for linha in f if linha.strip()]
        
        if not nomes:
            print("O ficheiro está vazio ou não contém nomes válidos.")
            return
        
        # Calcular comprimentos
        comprimentos = [len(nome) for nome in nomes]
        
        # Estatísticas
        nome_mais_pequeno = min(nomes, key=len)
        comprimento_mais_pequeno = len(nome_mais_pequeno)
        
        nome_mais_longo = max(nomes, key=len)
        comprimento_mais_longo = len(nome_mais_longo)
        
        comprimento_medio = sum(comprimentos) / len(comprimentos)
        # Exibir resultados
        print(f"Ficheiro analisado: {ficheiro}")
        print("-" * 40)
        print(f"Total de nomes encontrados: {len(nomes)}")
        print()
        print(f"Nome mais pequeno: '{nome_mais_pequeno}'")
        print(f"Comprimento: {comprimento_mais_pequeno} caracter(es)")
        print()
        print(f"Comprimento médio: {comprimento_medio:.2f} caracter(es) \n")
        print(f"Nome mais longo: '{nome_mais_longo}'")
        print(f"\n Comprimento: {comprimento_mais_longo} caracter(es)")
            
    except FileNotFoundError:
        print(f"Erro: O ficheiro '{ficheiro}' não foi encontrado.")
        print("Certifique-se de que o ficheiro existe no mesmo diretório do script.")
    except Exception as e:
        print(f"Erro ao ler o ficheiro: {e}")

# Executar a função
if __name__ == "__main__":
    analisar_nomes()