# ===============================
# ISEL | DEI | AMD
# Tiago Alcobia - 50521
# Miguel Alcobia - 50746
# Fábio Pestana - 50756
# ===============================

import pickle
import Orange
import json
import os
from collections import Counter
from datetime import datetime
import numpy as np

def get_dataset_info(dataset):
    """
    Exibe as informações básicas do dataset e a sua distribuição das classes.

    Args:
        dataset: Dataset a analisar.
    """

    # info básica
    print(f"Número de instâncias: {len(dataset)}")
    print(f"Número de atributos: {len(dataset.domain.attributes)}")
    print(f"Classe: {dataset.domain.class_var.name}")
    print(f"Valores da classe: {dataset.domain.class_var.values}")

    # Distribuição das classes
    class_distribution = Counter()
    for inst in dataset:
        class_value = str(inst.get_class())
        class_distribution[class_value] += 1

    print(f"\nDistribuição das classes: {dict(class_distribution)}")

def no_discretization_attributes_info(dataset):
    """
    Exibe as informações dos atributos de um dataset. Para cada atributo 
    presente no dataset, a função mostra:
      - O nome do atributo.
      - Os valores possíveis.
      - O tipo do atributo (discreto ou contínuo).
      - A distribuição de frequências dos valores observados no dataset.

    Args:
        dataset: Dataset a ser analisado.
    """
    for attr in dataset.domain.attributes:
        print(f"\n{attr.name}:")
        print(f"  Valores: {attr.values}")
        print(f"  Tipo: {'Discreto' if attr.is_discrete else 'Contínuo'}")
        
        # verificar frequência
        values_count = Counter()
        for inst in dataset:
            attr_value = str(inst[attr])
            values_count[attr_value] += 1

        print(f"  Distribuição: {dict(values_count)}")

def load_class_values(json_filepath):
    """
    Carrega a lista dos valores das classes armazenadas num ficheiro JSON.
    O ficheiro JSON deve conter uma chave "class_values" que lista as classes utilizadas
    no treino do modelo.

    Args:
        json_filepath: Caminho para o ficheiro JSON com as informações do modelo.

    Returns:
        list: Lista de valores de classes. Retorna uma lista vazia em caso de erro.
    """
    try:
        with open(json_filepath, 'r', encoding='utf-8') as f:
            model_info = json.load(f)
        
        class_values = model_info.get("class_values", [])
        #print(f"Valores das classes: {class_values}")
        return class_values
        
    except Exception as e:
        print(f"Erro ao carregar JSON: {e}")
        return []


def get_class_name_idx(idx, json_path):
    """
    Retorna o nome da classe segundo um índice (com base no ficheiro JSON do modelo).

    Args:
        idx: Índice da classe a obter.
        json_path: Caminho para o ficheiro JSON com as informações do modelo.

    Returns:
        class_values[idx]: Nome da classe correspondente ao índice.
    """
    class_values =  load_class_values(json_path)
    return class_values[idx]


def save_one_rule_to_json(results, dataset_filename, best_attr_name, output_dir="./train_result/rules"):
    """
    Guarda as regras geradas por um classificador OneRule num ficheiro JSON.
    O ficheiro inclui:
        - Nome do dataset.
        - Algoritmo utilizado (OneRule).
        - Melhor atributo encontrado.
        - Métricas de desempenho (instâncias totais, erros, taxa de erro, precisão).
        - Lista das regras geradas, com as respetivas condições, previsões e estatísticas.

    Args:
        results: Resultados do treino do classificador OneRule.
        dataset_filename: Caminho do ficheiro do dataset.
        best_attr_name: Nome do melhor atributo.
        output_dir: Caminho onde o ficheiro JSON será guardado (padrão: "./train_result/rules").

    Returns:
        filepath: Caminho do ficheiro JSON guardado.
    """
    
    if not results or best_attr_name not in results:
        print("Nenhum resultado para guardar.")
        return
    
    best_attr_data = results[best_attr_name]
    
    # Extrair nome do dataset sem extensão
    dataset_name = os.path.splitext(os.path.basename(dataset_filename))[0]
    
    # Gerar timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Criar nome do ficheiro
    filename = f"1R_{dataset_name}_{best_attr_name}_{timestamp}.json"
    
    # Criar diretório se não existir
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
    # Preparar dados para JSON
    rule_data = {
        "dataset": dataset_name,
        "algorithm": "OneRule",
        "best_attribute": best_attr_name,
        "timestamp": timestamp,
        "performance": {
            "total_instances": best_attr_data['total_instances'],
            "total_errors": best_attr_data['total_errors'],
            "error_rate": float(best_attr_data['error_rate']),  # Converter para float nativo
            "accuracy": float(best_attr_data['accuracy'])       # Converter para float nativo
        },
        "rules": []
    }
    
    # Adicionar todas as regras
    for _, rule_info in best_attr_data['rules'].items():
        rule = rule_info['rule']
        rule_data["rules"].append({
            "condition": f"{rule[0]} = '{rule[1]}'",
            "prediction": f"class = '{rule[2]}'",
            "feature": rule[0],
            "feature_value": rule[1],
            "predicted_class": rule[2],
            "errors": rule_info['errors'],
            "error_rate": float(rule_info['error_rate']),  # Converter para float nativo
            "instances_count": rule_info['total_count'],
            "correct_predictions": rule_info['max_count'],
            "class_distribution": rule_info['class_distribution']
        })
    
    # Guardar em JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(rule_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nRegra 1R guardada em: {filepath}")
    return filepath


def save_model_with_pickle(model, dataset_filename, model_type, class_values=None, output_dir="./train_result/models"):
    """
    Guarda um modelo treinado em ficheiros .pkl e .json.
    O ficheiro .pkl contém o objeto serializado do modelo, enquanto o ficheiro .json
    guarda informações complementares como o nome do dataset, tipo do modelo, data/hora
    e a lista das classes.

    Args:
        model: Modelo treinado a ser guardado.
        dataset_filename: Caminho do ficheiro do dataset utilizado no treino.
        model_type: Tipo de modelo ("DecisionTree", "GaussianNB" e "OneRule").
        class_values: Lista dos valores das classes (padrão: None).
        output_dir: Caminho onde os ficheiros vão ser guardados (padrão: "./train_result/models").

    Returns:
        pkl_filepath, json_filepath: Os caminhos dos ficheiros criados ou None em caso de erro.
    """
    
    if model is None:
        print(f"Modelo {model_type} inválido para guardar.")
        return None
    
    dataset_name = os.path.splitext(os.path.basename(dataset_filename))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"{model_type}_{dataset_name}_{timestamp}"
    
    os.makedirs(output_dir, exist_ok=True)
    
    pkl_filepath = os.path.join(output_dir, f"{base_filename}.pkl")
    
    try:
        with open(pkl_filepath, 'wb') as f:
            pickle.dump(model, f)
        
        print(f"\nModelo {model_type} guardado em: {pkl_filepath}")
        
    except Exception as e:
        print(f"Erro ao guardar modelo {model_type}: {e}")
        return None
    
    json_filepath = os.path.join(output_dir, f"{base_filename}.json")
    
    try:
        model_info = {
            "dataset": dataset_name,
            "model_type": model_type,
            "timestamp": timestamp,
            "class_values": class_values if class_values is not None else []
        }
        
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(model_info, f, indent=2, ensure_ascii=False)
        
        print(f"Informações do modelo guardadas em: {json_filepath}")
        
    except Exception as e:
        print(f"Erro ao guardar informações JSON do modelo: {e}")
    
    return pkl_filepath, json_filepath


def load_model_with_pickle(filepath):
    """
    Carrega um modelo guardado com pickle.
    
    Args:
        filepath: Caminho para o ficheiro .pkl.
    
    Returns:
        Modelo carregado ou None em caso de erro.
    """
    try:
        with open(filepath, 'rb') as f:
            model = pickle.load(f)
        return model
    except Exception as e:
        print(f"Erro ao carregar modelo: {e}")
        return None

def save_gaussian_nb_with_pickle(model, dataset_filename, class_values=None, output_dir="./train_result/models"):
    """
    Guarda um modelo Gaussian Naive Bayes em ficheiros .pkl e .json.

    Args:
        model: Modelo GaussianNB treinado.
        dataset_filename: Caminho do ficheiro do dataset utilizado no treino.
        class_values: Lista dos valores das classes (padrão: None).
        output_dir: Caminho onde os ficheiros vão ser guardados (padrão: "./train_result/models").

    Returns:
        pkl_filepath, json_filepath: Os caminhos dos ficheiros criados ou None em caso de erro.
    """
    return save_model_with_pickle(model, dataset_filename, "GaussianNB", class_values, output_dir)

def save_decision_tree_with_pickle(model, dataset_filename, class_values=None, output_dir="./train_result/models"):
    """
    Guarda um modelo Decision Tree em ficheiros .pkl e .json.

    Args:
        model: Modelo DecisionTree treinado.
        dataset_filename: Caminho do ficheiro do dataset utilizado no treino.
        class_values: Lista dos valores das classes (padrão: None).
        output_dir: Caminho onde os ficheiros vão ser guardados (padrão: "./train_result/models").

    Returns:
        pkl_filepath, json_filepath: Os caminhos dos ficheiros criados ou None em caso de erro.
    """
    return save_model_with_pickle(model, dataset_filename, "DecisionTree", class_values, output_dir)

def save_one_rule_with_pickle(model, dataset_filename, class_values=None, output_dir="./train_result/models"):
    """
    Guarda um modelo OneRule em ficheiros .pkl e .json.

    Args:
        model: Modelo OneRule treinado.
        dataset_filename: Caminho do ficheiro do dataset utilizado no treino.
        class_values: Lista dos valores das classes (padrão: None).
        output_dir: Caminho onde os ficheiros vão ser guardados (padrão: "./train_result/models").

    Returns:
        pkl_filepath, json_filepath: Os caminhos dos ficheiros criados ou None em caso de erro.
    """
    return save_model_with_pickle(model, dataset_filename, "OneRule", class_values, output_dir)