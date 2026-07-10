# Tiago Alcobia - 50521
# Miguel Alcobia - 50746
# Fábio Pestana - 50756

from collections import Counter
import math
import sys
import a01_dataset_analysis as da
import aux_data_preparation as dp
from e_Config import e_Config

# ===============================
# ESTRUTURAS DE DADOS PARA ÁRVORE DE DECISÃO
# ===============================

class TreeNode:
    """Nó da árvore de decisão"""
    def __init__(self, attribute=None, is_leaf=False, class_value=None):
        self.attribute = attribute  # Atributo testado neste nó
        self.is_leaf = is_leaf      # Se é nó folha
        self.class_value = class_value  # Valor da classe (se folha)
        self.children = {}          # Filhos: {valor_atributo: TreeNode}
        self.majority_class = None  # Classe majoritária no nó
    
    def add_child(self, value, child_node):
        """Adiciona um filho ao nó"""
        self.children[value] = child_node
    
    def __str__(self, level=0):
        """Representação em string da árvore"""
        indent = "  " * level
        if self.is_leaf:
            return f"{indent}Classe: {self.class_value}\n"
        else:
            result = f"{indent}{self.attribute}?\n"
            for value, child in self.children.items():
                result += f"{indent}-> {value}:\n"
                result += child.__str__(level + 1)
            return result

# ===============================
# ALGORITMO ID3
# ===============================

class ID3DecisionTree:
    def __init__(self, min_samples_split=2):
        self.min_samples_split = min_samples_split
        self.root = None
    
    def fit(self, dataset):
        """
        Constrói a árvore de decisão usando o algoritmo ID3.
        """
        print("\n" + "="*50)
        print("====== ID3 DECISION TREE ALGORITHM ======")
        print("="*50)
        
        attributes = dataset.domain.attributes
        class_var = dataset.domain.class_var
        
        # Construir a árvore recursivamente
        self.root = self._build_tree(dataset, attributes, class_var, depth=0)
        
        print("\n--- ÁRVORE DE DECISÃO CONSTRUÍDA ---")
        print(self.root)
        
        return self.root
    
    def _build_tree(self, dataset, attributes, class_var, depth):
        """
        Constrói a árvore recursivamente usando o algoritmo ID3.
        """
        # Contar distribuição das classes no dataset atual
        class_distribution = self._get_class_distribution(dataset, class_var)
        
        # CASO 1: Todos os exemplos pertencem à mesma classe
        if len(class_distribution) == 1:
            class_value = list(class_distribution.keys())[0]
            leaf_node = TreeNode(is_leaf=True, class_value=class_value)
            leaf_node.majority_class = class_value
            print(f"{'  ' * depth}CASO 1: Todos exemplos são da classe '{class_value}'")
            return leaf_node
        
        # CASO 2: Não há mais atributos para testar
        if not attributes:
            majority_class = max(class_distribution.items(), key=lambda x: x[1])[0]
            leaf_node = TreeNode(is_leaf=True, class_value=majority_class)
            leaf_node.majority_class = majority_class
            print(f"{'  ' * depth}CASO 2: Sem atributos, classe majoritária '{majority_class}'")
            return leaf_node
        
        # CASO 3: Número mínimo de exemplos não atingido
        if len(dataset) < self.min_samples_split:
            majority_class = max(class_distribution.items(), key=lambda x: x[1])[0]
            leaf_node = TreeNode(is_leaf=True, class_value=majority_class)
            leaf_node.majority_class = majority_class
            print(f"{'  ' * depth}CASO 3: Poucos exemplos ({len(dataset)}), classe majoritária '{majority_class}'")
            return leaf_node
        
        # Escolher o melhor atributo usando Information Gain
        best_attribute = self._choose_best_attribute(dataset, attributes, class_var, depth)
        
        print(f"{'  ' * depth}✓ MELHOR ATRIBUTO: {best_attribute.name} (Information Gain mais alto)")
        
        # Criar nó de decisão
        node = TreeNode(attribute=best_attribute.name)
        node.majority_class = max(class_distribution.items(), key=lambda x: x[1])[0]
        
        # Remover o atributo escolhido da lista de atributos disponíveis
        remaining_attributes = [attr for attr in attributes if attr != best_attribute]
        
        # Para cada valor do atributo escolhido, criar um filho
        for value in best_attribute.values:
            # Filtrar dataset para exemplos com este valor do atributo
            subset = [inst for inst in dataset if str(inst[best_attribute]) == value]
            
            if not subset:
                # Se não há exemplos, criar folha com classe majoritária do pai
                majority_class = max(class_distribution.items(), key=lambda x: x[1])[0]
                child_node = TreeNode(is_leaf=True, class_value=majority_class)
                child_node.majority_class = majority_class
                print(f"{'  ' * (depth+1)}Valor '{value}': Sem exemplos, usar classe pai '{majority_class}'")
            else:
                # Construir sub-árvore recursivamente
                print(f"{'  ' * (depth+1)}Valor '{value}': {len(subset)} exemplos")
                child_node = self._build_tree(subset, remaining_attributes, class_var, depth + 2)
            
            node.add_child(value, child_node)
        
        return node
    
    def _choose_best_attribute(self, dataset, attributes, class_var, depth):
        """
        Escolhe o atributo com maior Information Gain.
        """
        # Calcular entropia do dataset atual
        current_entropy = self._calculate_entropy(dataset, class_var)
        
        print(f"{'  ' * depth}Entropia atual: {current_entropy:.4f}")
        print(f"{'  ' * depth}Avaliando atributos:")
        
        best_gain = -1
        best_attribute = None
        
        for attr in attributes:
            # Calcular Information Gain para este atributo
            gain = self._calculate_information_gain(dataset, attr, class_var, current_entropy)
            
            print(f"{'  ' * (depth+1)}- {attr.name}: Gain = {gain:.4f}")
            
            if gain > best_gain:
                best_gain = gain
                best_attribute = attr
        
        return best_attribute
    
    def _calculate_entropy(self, dataset, class_var):
        """
        Calcula a entropia do dataset para a variável de classe.
        """
        if len(dataset) == 0:
            return 0
        
        class_counts = Counter()
        for instance in dataset:
            class_value = str(instance[class_var])
            class_counts[class_value] += 1
        
        entropy = 0
        for count in class_counts.values():
            probability = count / len(dataset)
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _calculate_information_gain(self, dataset, attribute, class_var, current_entropy):
        """
        Calcula o Information Gain para um atributo.
        """
        if len(dataset) == 0:
            return 0
        
        # Particionar dataset pelos valores do atributo
        partitions = {}
        for instance in dataset:
            attr_value = str(instance[attribute])
            if attr_value not in partitions:
                partitions[attr_value] = []
            partitions[attr_value].append(instance)
        
        # Calcular entropia ponderada
        weighted_entropy = 0
        for value, subset in partitions.items():
            subset_entropy = self._calculate_entropy(subset, class_var)
            weight = len(subset) / len(dataset)
            weighted_entropy += weight * subset_entropy
        
        # Information Gain = entropia_atual - entropia_ponderada
        information_gain = current_entropy - weighted_entropy
        return information_gain
    
    def _get_class_distribution(self, dataset, class_var):
        """
        Retorna a distribuição das classes no dataset.
        """
        distribution = Counter()
        for instance in dataset:
            class_value = str(instance[class_var])
            distribution[class_value] += 1
        return distribution
    
    def predict(self, instance):
        """
        Classifica uma instância usando a árvore de decisão.
        """
        if self.root is None:
            raise ValueError("Árvore não foi treinada. Chame fit() primeiro.")
        
        return self._predict_recursive(instance, self.root)
    
    def _predict_recursive(self, instance, node):
        """
        Função recursiva para percorrer a árvore e fazer predição.
        """
        # Se é nó folha, retorna a classe
        if node.is_leaf:
            return node.class_value
        
        # Obter o valor do atributo na instância
        attribute_value = str(instance[node.attribute])
        
        # Verificar se há filho para este valor
        if attribute_value in node.children:
            child_node = node.children[attribute_value]
            return self._predict_recursive(instance, child_node)
        else:
            # Valor não visto durante treino, usar classe majoritária do nó
            print(f"AVISO: Valor '{attribute_value}' não encontrado para atributo '{node.attribute}'. Usando classe majoritária.")
            return node.majority_class
    
    def evaluate(self, dataset):
        """
        Avalia a árvore no dataset completo.
        """
        if self.root is None:
            raise ValueError("Árvore não foi treinada. Chame fit() primeiro.")
        
        class_var = dataset.domain.class_var
        correct = 0
        total = len(dataset)
        
        print(f"\n--- AVALIAÇÃO DA ÁRVORE DE DECISÃO ---")
        print(f"Total de instâncias: {total}")
        
        for i, instance in enumerate(dataset):
            true_class = str(instance[class_var])
            predicted_class = self.predict(instance)
            
            if predicted_class == true_class:
                correct += 1
            
            # Mostrar detalhes das primeiras predições
            if i < 5:
                status = "✓" if predicted_class == true_class else "✗"
                print(f"Instância {i+1}: {true_class} → {predicted_class} {status}")
        
        accuracy = correct / total if total > 0 else 0
        print(f"\nAcurácia total: {correct}/{total} = {accuracy:.4f}")
        
        return accuracy

# ===============================
# FUNÇÃO PRINCIPAL DO ALGORITMO
# ===============================

def id3_algorithm(dataset, min_samples_split=2):
    """
    Função principal do algoritmo ID3.
    """
    tree_classifier = ID3DecisionTree(min_samples_split=min_samples_split)
    tree = tree_classifier.fit(dataset)
    accuracy = tree_classifier.evaluate(dataset)
    
    return tree_classifier, accuracy

# ===============================
# FUNÇÕES AUXILIARES PARA ANÁLISE
# ===============================

def analyze_attribute_gain(dataset):
    """
    Analisa o Information Gain de todos os atributos.
    """
    print("\n" + "="*50)
    print("ANÁLISE DE INFORMATION GAIN POR ATRIBUTO")
    print("="*50)
    
    attributes = dataset.domain.attributes
    class_var = dataset.domain.class_var
    
    # Calcular entropia do dataset completo
    classifier = ID3DecisionTree()
    current_entropy = classifier._calculate_entropy(dataset, class_var)
    
    print(f"Entropia do dataset completo: {current_entropy:.4f}")
    print(f"Número de instâncias: {len(dataset)}")
    print(f"Distribuição das classes: {dict(classifier._get_class_distribution(dataset, class_var))}")
    
    gains = []
    for attr in attributes:
        gain = classifier._calculate_information_gain(dataset, attr, class_var, current_entropy)
        gains.append((attr.name, gain))
        print(f"  {attr.name}: {gain:.4f}")
    
    # Ordenar por gain descendente
    gains.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\nATRIBUTOS ORDENADOS POR INFORMATION GAIN:")
    for attr_name, gain in gains:
        print(f"  {attr_name}: {gain:.4f}")
    
    return gains

# ===============================
# MAIN
# ===============================

def main():
    config = e_Config()
    config.config(sys.argv)
    file_name = config.get_file_path()
    
    # Carregar dataset
    dataset = da.load(file_name)
    if dataset is None:
        exit()
    
    dp.get_dataset_info(dataset)
    dp.no_discretization_attributes_info(dataset)
    
    # Análise de Information Gain
    analyze_attribute_gain(dataset)
    
    # Executar algoritmo ID3
    tree_classifier, accuracy = id3_algorithm(dataset, min_samples_split=2)
    
    # Testar predições
    print("\n" + "="*50)
    print("TESTE DE PREDIÇÕES")
    print("="*50)
    
    # Testar com algumas instâncias do dataset
    for i in range(min(3, len(dataset))):
        instance = dataset[i]
        true_class = str(instance[dataset.domain.class_var])
        predicted_class = tree_classifier.predict(instance)
        
        print(f"Instância {i+1}:")
        print(f"  Verdadeiro: {true_class}")
        print(f"  Previsto:   {predicted_class}")
        print(f"  Status: {'✓ CORRETO' if true_class == predicted_class else '✗ ERRADO'}")
        print()
    
    return tree_classifier, accuracy

# ===============================
# EXECUÇÃO
# ===============================
if __name__ == "__main__":
    tree_classifier, accuracy = main()