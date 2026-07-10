# ===============================
# ISEL | DEI | AMD
# Tiago Alcobia - 50521
# Miguel Alcobia - 50746
# Fábio Pestana - 50756
# ===============================

import sys
from u01_util import my_print
import Orange as DM

def load_dataset(file_name):
    """
    Carrega o dataset segundo o caminho recebido.

    Args:
        file_name: Caminho do dataset a carregar.

    Returns:
        dataset: Dataset carregado
    """
    try:
        dataset = DM.data.Table(file_name)
        return dataset
    except:
        my_print("--->>> error - can not open the file: %s" % file_name)
        return None


def display_dataset_info(dataset):
    """
    Exibe informações gerais do dataset.
    
    Args:
        dataset: Dataset a analisar
    """
    print("=" * 10)
    print(dataset)
    print("=" * 10)
    print(dataset.domain)
    print("=" * 10)
    print(dataset.domain.variables)
    print("=" * 10)
    print(dataset.domain.attributes)
    print("=" * 10)
    print(dataset.domain.class_var)
    print("=" * 10)


def analyze_variables(dataset):
    """
    Analisa as variáveis (atributos) do dataset.
    
    Args:
        dataset: Dataset a analisar
    """
    variable_list = dataset.domain.attributes
    my_print(aStr=">> %d Variables (attributes+class) <<" % len(variable_list))
    print(">> name (type): (value1, value2, ...) <<")
    
    n_disc = 0
    n_cont = 0
    n_str = 0
    
    for variable in variable_list:
        print(":: %s %s" % (variable.name, variable.TYPE_HEADERS), end=""),
        if variable.is_discrete:
            print(": {0} ".format(variable.values))
            n_disc += 1
        elif variable.is_continuous:
            print()
            n_cont += 1
        else:
            n_str += 1
    
    my_print(">> Types: %d discrete, %d continuous <<" % (n_disc, n_cont))
    
    return n_disc, n_cont, n_str


def analyze_class(dataset):
    """
    Analisa a variável classe do dataset.
    
    Args:
        dataset: Dataset a analisar
    """
    the_class = dataset.domain.class_var
    my_print(">> Class <<")
    print(":: %s %s: %s " % (the_class.name,
                             the_class.TYPE_HEADERS,
                             the_class.values))

def display_first_instances(dataset, n=10):
    """
    Exibe as primeiras N instâncias do dataset.
    
    Args:
        dataset: Dataset a analisar
        n (int): Número de instâncias a exibir
    """
    my_print("First %d instances:" % n)
    for i in range(n):
        print(dataset[i])

def main():
    # Obter nome do arquivo
    file_name = "./_datasets/lenses_3RowHeader.tab"
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    
    # Carregar dataset
    dataset = load_dataset(file_name)
    if dataset is None:
        exit()
    
    # Executar análises
    display_dataset_info(dataset)
    analyze_variables(dataset)
    analyze_class(dataset)
    display_first_instances(dataset, 10)

# ===============================
# EXECUÇÃO
# ===============================
if __name__ == "__main__":
    main()