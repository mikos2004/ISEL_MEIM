# Tiago Alcobia - 50521
# Miguel Alcobia - 50746
# Fábio Pestana - 50756

from collections import Counter
import sys
import numpy as np
import Orange as DM
#import a01_datasetRead as dr
import a01_dataset_analysis as da
import aux_data_preparation as dp
from e_Config import e_Config

# ===============================
# CLASSE ONE RULE
# ===============================
class OneRule:
    def __init__(self, dataset=None):
        """
        Construtor da classe OneRule.
        
        Args:
            dataset: Dataset para análise (opcional, pode ser definido depois)
        """
        self.dataset = dataset
        self.attributes = dataset.domain.attributes if dataset else None
        self.class_var = dataset.domain.class_var if dataset else None
        self.results = {}
        self.best_attr_name = None
        self.best_attr_data = None
        self.feature_names_ = None
        self.classes_ = None
    
    def _convert_to_orange_dataset(self, X, y, feature_names=None, class_names=None):
        """
        Converte arrays numpy (X, y) para um dataset Orange.
        
        Args:
            X: Array de features
            y: Array de classes
            feature_names: Nomes das features
            class_names: Nomes das classes
            
        Returns:
            Orange dataset
        """
        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(X.shape[1])]
        
        if class_names is None:
            class_names = list(map(str, np.unique(y)))
        
        features = []
        for i, name in enumerate(feature_names):
            # Determinar se é discreto ou contínuo
            unique_vals = np.unique(X[:, i])
            if len(unique_vals) <= 10 or all(isinstance(x, str) for x in unique_vals):
                feature = DM.data.DiscreteVariable(name, values=list(map(str, unique_vals)))
            else:
                feature = DM.data.ContinuousVariable(name)
            features.append(feature)
        
        class_var = DM.data.DiscreteVariable("class", values=class_names)
        domain = DM.data.Domain(features, class_var)
        
        # Converter dados
        orange_data = []
        for i in range(len(X)):
            row = list(X[i]) + [y[i]]
            orange_data.append(row)
        
        return DM.data.Table(domain, orange_data)

    def analyze_attribute(self, attr):
        """
        Analisa um atributo específico e gera as regras 1R.
        
        Args:
            attr: Atributo a ser analisado
            
        Returns:
            dict: Dados das regras e estatísticas do atributo
        """
        print(f"\n--- Analise do atributo: {attr.name} ---")
        attr_values = attr.values
        rules = {}
        total_errors = 0
        total_instances = 0

        # ii. para cada um dos seus valores, atr-v
        for attr_value in attr_values:
            # iii. obter a frequência, k, com que atr-v se associa a cada valor, c-v, da classe
            class_counts = Counter() # dicionário que ficará com o valor e sua freq

            for instance in self.dataset:
                if str(instance[attr]) == attr_value:
                    class_value = str(instance[self.class_var])
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

        # viii. calcular #erros por atributo
        attr_error_rate = total_errors / total_instances if total_instances > 0 else 1.0
        
        attr_results = {
            'rules': rules,
            'total_errors': total_errors,
            'total_instances': total_instances,
            'error_rate': attr_error_rate,
            'accuracy': 1.0 - attr_error_rate
        }
        
        print(f"--- RESUMO {attr.name}: {total_errors} erros em {total_instances} instâncias "
                f"(taxa: {attr_error_rate:.3f}, Taxa de Sucesso: {1.0 - attr_error_rate:.3f}) ---")
        
        return attr_results

    def fit(self, X, y, feature_names=None, class_names=None):
        """
        Treina o modelo

        Args:
            X: features do conjunto de treino
            y: classe do conjunto de treino
            feature_names: Nomes das features.
            class_names: Nome da classe.

        Returns:
            results, best_attr: resultados do fit e o melhor atributo
        """
        
        # Converter para dataset Orange
        self.dataset = self._convert_to_orange_dataset(X, y, feature_names, class_names)
        self.attributes = self.dataset.domain.attributes
        self.class_var = self.dataset.domain.class_var
        self.feature_names_ = [attr.name for attr in self.attributes]
        self.classes_ = self.class_var.values

        print("\n================================")
        print("====== ONE RULE ALGORITHM ======")
        print("================================")

        # i. para cada atributo, atr
        for attr in self.attributes:
            # 1R só funciona com atributos discretos
            if not attr.is_discrete:
                print(f"  Atributo '{attr.name}' não é discreto")
                continue

            # Analisar o atributo
            self.results[attr.name] = self.analyze_attribute(attr)

        # ix. escolher o atributo com menor #erros
        if self.results:
            best_attr = min(self.results.items(), key=lambda x: x[1]['error_rate'])
            self.best_attr_name = best_attr[0]
            self.best_attr_data = best_attr[1]
            
            self._print_results()
        else:
            print("Nenhum atributo encontrado para análise 1R")
            
        return self.results, best_attr

    def predict(self, X):
        """
        Método que realiza a previsão do conjunto recebido.

        Args:
            X: features do conjunto de teste

        Raises:
            ValueError: Caso não exista um "melhor atributo"
            ValueError: Caso o "melhor atributo" não seja analisado
        
        Returns:
            predictions: array com as previsões
        """
        if self.best_attr_name is None:
            raise ValueError("Nenhum atributo foi definido para o predict. Treine com o fit() primeiro.")
        
        if self.best_attr_name not in self.results:
            raise ValueError(f"Atributo '{self.best_attr_name}' não foi analisado.")
        
        # Encontrar o atributo correspondente
        attr_idx = None
        for i, attr in enumerate(self.attributes):
            if attr.name == self.best_attr_name:
                attr_idx = i
                break
        
        predictions = []
        
        for instance_features in X:
            # Obter o valor do atributo na instância
            attr_value = str(instance_features[attr_idx])
            
            # Encontrar a regra correspondente
            if attr_value in self.results[self.best_attr_name]['rules']:
                rule_data = self.results[self.best_attr_name]['rules'][attr_value]
                predicted_class = rule_data['rule'][2]  # Classe predita
            else:
                # Se o valor não foi visto durante o treino, retorna a classe mais frequente globalmente
                class_counts = Counter(str(inst[self.class_var]) for inst in self.dataset)
                predicted_class = class_counts.most_common(1)[0][0]
            
            predictions.append(predicted_class)
        
        return np.array(predictions)

    def _print_results(self):
        """
        Imprime os resultados do melhor atributo.
        """

        print("\n" + "="*50)
        print(">>> MELHOR ATRIBUTO PARA 1R <<<\n")
        print(f"Atributo: {self.best_attr_name}")
        print(f"Taxa de erro: {self.best_attr_data['error_rate']:.3f}")
        print(f"Taxa de Sucesso: {self.best_attr_data['accuracy']:.3f}")
        print(f"Total de instâncias: {self.best_attr_data['total_instances']}")
        print(f"Total de erros: {self.best_attr_data['total_errors']}")
        
        print("\n>>> REGRAS 1R PARA O MELHOR ATRIBUTO <<<")
        for _, rule_data in self.best_attr_data['rules'].items():
            rule = rule_data['rule']
            print(f"SE {rule[0]} = '{rule[1]}' ENTÃO classe = '{rule[2]}' "
                    f"(erros: {rule_data['errors']}, taxa: {rule_data['error_rate']:.3f})")
        
        print("="*50)

def main():
    config = e_Config()
    config.config(sys.argv)
    file_name = config.get_file_path()
    
    # Carregar dataset
    dataset = da.load(file_name)
    if dataset is None:
        exit()
    
    one_rule = OneRule()
    results, best_attr = one_rule.fit(dataset.X, dataset.Y)
    
    # Guardar regra em JSON (atualizado)
    if best_attr:
        best_attr_name = best_attr[0]  # Extrair o nome do melhor atributo
        dp.save_one_rule_to_json(results, file_name, best_attr_name)


# ===============================
# EXECUÇÃO
# ===============================
if __name__ == "__main__":
    main()