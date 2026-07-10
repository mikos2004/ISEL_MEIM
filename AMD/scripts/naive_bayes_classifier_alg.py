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
# ALGORITMO NAIVE BAYES
# ===============================
class NaiveBayesClassifier():
    def __init__(self):
        """
        Construtor da classe NaiveBayesClassifier.
        Inicializa o classificador com valores padrões.
        """
        self.laplace_estimator = 1
        self.class_probabilities = {}
        self.attribute_probabilities = {}
        self.numeric_stats = {}
        
    def fit(self, dataset):
        """
        Treina o modelo Naive Bayes segundo o dataset introduzido.

        Calcula:
            - As probabilidades a priori de cada classe.
            - As probabilidade condicionais de cada atributo relativamente a cada classe.
        
        Args:
            dataset: dataset contendo os atributos e a variável de classe.
        """
        print("\n" + "="*50)
        print("====== NAIVE BAYES CLASSIFIER ======")
        print("="*50)
        
        attributes = dataset.domain.attributes
        class_var = dataset.domain.class_var
        
        # Frequências das classes
        class_counts = Counter()
        for instance in dataset:
            class_value = str(instance[class_var])
            class_counts[class_value] += 1
        
        total_instances = len(dataset)
        
        # Prob. a priori das classes
        self.class_probabilities = {}
        for class_value, count in class_counts.items():
            self.class_probabilities[class_value] = count / total_instances
        
        print(f"\n--- Prob. a priori das classes ---")
        for class_value, prob in self.class_probabilities.items():
            print(f"  P({class_var.name}='{class_value}') = {prob:.4f} ({class_counts[class_value]}/{total_instances})")
        
        # Calcular prob. condicionais para cada atributo
        self.attribute_probabilities = {}
        self.numeric_stats = {}
        
        for attr in attributes:
            print(f"\n--- Probabilidades condicionais para: {attr.name} ---")
            
            if attr.is_discrete:
                # Atributo discreto
                attr_probs = self._calculate_discrete_probabilities(dataset, attr, class_var, class_counts)
                self.attribute_probabilities[attr.name] = attr_probs
                
                for attr_value in attr.values:
                    print(f"  Valor '{attr_value}':")
                    for class_value in class_counts.keys():
                        prob = attr_probs.get((attr_value, class_value), 0)
                        print(f"    P({attr.name}='{attr_value}'|{class_var.name}='{class_value}') = {prob:.4f}")
            
            else:
                # Atributo numérico -> média e desvio padrão
                numeric_stats = self._calculate_numeric_statistics(dataset, attr, class_var, class_counts)
                self.numeric_stats[attr.name] = numeric_stats
                
                print(f"  Distribuição normal (Gaussiana):")
                for class_value in class_counts.keys():
                    if class_value in numeric_stats:
                        mean, std = numeric_stats[class_value]
                        print(f"    Classe '{class_value}': mean={mean:.4f}, std={std:.4f}")
    
    def _calculate_discrete_probabilities(self, dataset, attr, class_var, class_counts):
        """
        Calcula probabilidade condicionada para atributos discretos.

        Args:
            dataset: Dataset de treino.
            attr: Atributo a analisar.
            class_var: Variável da classe.
            class_counts: Número de instâncias por classe.

        Returns:
            Dicionário no formato {(valor_do_atributo, classe): probabilidade}.
        """
        probabilities = {}
        
        for attr_value in attr.values:
            for class_value in class_counts.keys():
                # Contar ocorrências do par (valor_atributo, classe)
                count = 0
                for instance in dataset:
                    if (str(instance[attr]) == attr_value and 
                        str(instance[class_var]) == class_value):
                        count += 1
                
                # Aplicar suavização de Laplace
                total_class_count = class_counts[class_value]
                prob = (count + self.laplace_estimator) / (total_class_count + self.laplace_estimator * len(attr.values))
                probabilities[(attr_value, class_value)] = prob
        
        return probabilities
    
    def _calculate_numeric_statistics(self, dataset, attr, class_var, class_counts):
        """
        Calcula média e desvio padrão para atributos numéricos.

        Args:
            dataset: Dataset de treino.
            attr: Atributo a analisar.
            class_var: Variável da classe.
            class_counts: Número de instâncias por classe.

        Returns:
            Dicionário no formato {classe: (média, desvio_padrão)}.
        """
        stats = {}
        
        for class_value in class_counts.keys():
            # Valores do atributo para a classe
            values = []
            for instance in dataset:
                if str(instance[class_var]) == class_value:
                    value = float(instance[attr])
                    values.append(value)
            
            if values:
                mean = sum(values) / len(values)
                
                # desvio padrão
                variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1) if len(values) > 1 else 0
                std = math.sqrt(variance) if variance > 0 else 0.0001  # para evitar divisão por zero
                
                stats[class_value] = (mean, std)
        
        return stats
    
    def _normal_prob_dist(self, x, mean, std):
        """
        Calcula a função de densidade de probabilidade da distribuição normal.

        Args:
            x: Valor a avaliar.
            mean: Valor da média.
            std: Valor do desvio padrão.

        Returns:
            Resultado do cálculo da função de densidade de probabilidade da distribuição normal.
        """
        if std == 0:
            std = 0.0001  # para evitar dividir por zero
        
        exponent = math.exp(-((x - mean) ** 2) / (2 * std ** 2))
        return (1 / (std * math.sqrt(2 * math.pi))) * exponent
    
    def predict(self, instance):
        """
        Método que realiza a previsão de uma instância.

        Args:
            instance: Instância a classificar.
        
        Returns:
            (predicted_class, probabilities): Classe prevista e probabilidades normalizadas por classe.
        """

        probabilities = {}
        
        for class_value, prior_prob in self.class_probabilities.items():
            # Começar com probabilidade a priori
            posterior_prob = prior_prob
            
            # Multiplicar probabilidades condicionais
            for attr_name in self.attribute_probabilities:
                attr_value = str(instance[attr_name])
                # valor default para evitar erro
                cond_prob = self.attribute_probabilities[attr_name].get((attr_value, class_value), pow(10, -10))
                posterior_prob *= cond_prob
            
            # Atributos numéricos
            for attr_name in self.numeric_stats:
                if class_value in self.numeric_stats[attr_name]:
                    numeric_value = float(instance[attr_name])
                    mean, std = self.numeric_stats[attr_name][class_value]
                    density = self._normal_prob_dist(numeric_value, mean, std)
                    posterior_prob *= density
            
            probabilities[class_value] = posterior_prob
        
        # Normalizar
        total = sum(probabilities.values())
        if total > 0:
            for class_value in probabilities:
                probabilities[class_value] /= total
        
        predicted_class = max(probabilities.items(), key=lambda x: x[1])[0]
        return predicted_class, probabilities
    


def naive_bayes_algorithm(dataset):
    """
    Executa o algoritmo Naive Bayes segundo um dataset.

    Args:
        dataset: Dataset de treino.
        
    Returns:
        classifier: Modelo treinado.
    """
    classifier = NaiveBayesClassifier()
    classifier.fit(dataset)
    
    return classifier

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
    
    #dp.get_dataset_info(dataset)
    #dp.no_discretization_attributes_info(dataset)

    # Executar algoritmo Naive Bayes
    classifier = naive_bayes_algorithm(dataset)

    print("\n" + "="*60)
    print("TESTE DE CLASSIFICAÇÃO - INSTÂNCIAS DO DATASET")
    print("="*60)
    
    # Teste com algumas instâncias
    for i in range(min(6, len(dataset))):
        instance = dataset[i]
        true_class = str(instance[dataset.domain.class_var])
        predicted_class, probabilities = classifier.predict(instance)
        
        print(f"\nInstância {i+1}:")
        print(f"  Verdadeiro: {true_class}")
        print(f"  Previsto:   {predicted_class}")
        print(f"  Probabilidades: {probabilities}")
        print(f"  CORRETO" if true_class == predicted_class else "  ERRADO")
    
    #dp.save_naive_bayes_to_json(classifier, file_name)

# ===============================
# EXECUÇÃO
# ===============================
if __name__ == "__main__":
    main()