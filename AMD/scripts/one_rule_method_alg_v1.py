# Tiago Alcobia - 50521
# Miguel Alcobia - 50746
# Fábio Pestana - 50756

from collections import Counter
import sys
#import a01_datasetRead as dr
import a01_dataset_analysis as da
from e_Config import e_Config

# ===============================
# ALGORITMO 1R
# ===============================
def one_rule_algorithm(dataset):
    """
    Implementa o algoritmo 1R (One Rule) para classificação.

    Args:
    dataset: Dataset a analisar

    Returns:
    dict: Resultados do algoritmo 1R
    """
    attributes = dataset.domain.attributes
    class_var = dataset.domain.class_var

    results = {}

    # com base nos slies:
    # i. para cada atributo, atr
    for attr in attributes:
        # 1R só funciona com atributos discretos
        if not attr.is_discrete:
            continue

        print(f"\n--- Analise do atributo: {attr.name} ---")
        attr_values = attr.values
        rules = {}
        total_errors = 0
        total_instances = 0

        # ii. para cada um dos seus valores, atr-v
        for attr_value in attr_values:
            # iii. obter a frequência, k, com que atr-v se associa a cada valor, c-v, da classe
            class_counts = Counter() # dicionário que ficará com o valor e sua freq

            for instance in dataset:
                if str(instance[attr]) == attr_value:
                    class_value = str(instance[class_var])
                    class_counts[class_value] += 1
                
            if class_counts:  # Se há instâncias com este valor do atributo
                # iv. encontrar o par (atr-v, k) com valor mais alto de k
                most_common_class, max_count = class_counts.most_common(1)[0]
                total_count = sum(class_counts.values())

                # v. construir a regra que consiste em associar o tuplo: (atr, atr-v, c-v)
                rule = (attr.name, attr_value, most_common_class)

                # vi. calcular #erros de cada regra
                errors = total_count - max_count
                error_rate = errors / total_count if total_count > 0 else 0

                rules[attr_value] = {
                    'rule': rule,
                    'total_count': total_count,
                    'max_count': max_count,
                    'errors': errors,
                    'error_rate': error_rate,
                    'class_distribution': dict(class_counts)
                }

                total_errors += errors
                total_instances += total_count

                print(f"  Valor '{attr_value}': {total_count} instâncias")
                print(f"    Classe mais frequente: '{most_common_class}' ({max_count} ocorrências)")
                print(f"    Erros: {errors} (taxa: {error_rate:.3f})")
                print(f"    Distribuição: {dict(class_counts)}")

        # vii. para cada atributo, as regras (uma por valor do atributo) já foram escolhidas
        # com base na classe mais frequente (menor erro por valor)
        # Aqui, mantemos todas essas regras e usaremos o erro total no passo seguinte.
        
        # viii. calcular #erros por atributo
        attr_error_rate = total_errors / total_instances if total_instances > 0 else 1.0
        
        results[attr.name] = {
            'rules': rules,
            'total_errors': total_errors,
            'total_instances': total_instances,
            'error_rate': attr_error_rate,
            'accuracy': 1.0 - attr_error_rate
        }
        
        print(f"--- RESUMO {attr.name}: {total_errors} erros em {total_instances} instâncias "
                f"(taxa: {attr_error_rate:.3f}, Precisão: {1.0 - attr_error_rate:.3f}) ---")
    
    # ix. escolher o atributo com menor #erros
    if results:
        best_attr = min(results.items(), key=lambda x: x[1]['error_rate'])
        best_attr_name = best_attr[0]
        best_attr_data = best_attr[1]
        
        print("\n" + "="*50)
        print(">>> MELHOR ATRIBUTO PARA 1R <<<")
        print(f"Atributo: {best_attr_name}")
        print(f"Taxa de erro: {best_attr_data['error_rate']:.3f}")
        print(f"Precisão: {best_attr_data['accuracy']:.3f}")
        print(f"Total de instâncias: {best_attr_data['total_instances']}")
        print(f"Total de erros: {best_attr_data['total_errors']}")
        
        print("\n>>> REGRAS 1R PARA O MELHOR ATRIBUTO <<<")
        for attr_value, rule_data in best_attr_data['rules'].items():
            rule = rule_data['rule']
            print(f"SE {rule[0]} = '{rule[1]}' ENTÃO classe = '{rule[2]}' "
                    f"(erros: {rule_data['errors']}, taxa: {rule_data['error_rate']:.3f})")
        
        print("="*50)
    
    return results


def main():
    """
    Função principal que orquestra a análise do dataset.
    """
    config = e_Config()
    config.config(sys.argv)
    file_name = config.get_file_path()
    
    # Carregar dataset
    dataset = da.load(file_name)
    if dataset is None:
        exit()
    
    # Executar algoritmo 1R
    results = one_rule_algorithm(dataset)



# ===============================
# EXECUÇÃO
# ===============================
if __name__ == "__main__":
    main()