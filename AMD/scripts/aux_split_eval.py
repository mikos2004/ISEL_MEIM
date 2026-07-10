# Tiago Alcobia - 50521
# Miguel Alcobia - 50746
# Fábio Pestana - 50756

# Baseado em funções dos slides do prof. Paulo Trigo

import Orange
from sklearn.calibration import label_binarize
from sklearn.metrics import accuracy_score, auc, cohen_kappa_score, f1_score, precision_score, recall_score, confusion_matrix, ConfusionMatrixDisplay, roc_curve
from sklearn.model_selection import KFold, LeaveOneOut, LeavePOut, RepeatedKFold, RepeatedStratifiedKFold, ShuffleSplit, StratifiedKFold, StratifiedShuffleSplit
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from mybootstrap import MyBootstrapSplitOnce, MyBootstrapSplitRepeated
import numpy as np
import matplotlib .pyplot as plt

from naive_bayes_classifier_alg import NaiveBayesClassifier
from one_rule_method_alg_v2 import OneRule

import aux_data_preparation as dp


def orange_to_numpy(dataset_path):
    """
    Carrega um dataset no formato Orange e converte para um array do Numpy.
    A função lê um ficheiro de dataset compatível com o Orange e devolve o
    objeto Orange.data.Table e os arrays Numpy correspondente às features (X) e 
    às classes (y).

    Args:
        dataset_path: Caminho para o ficheiro do dataset.

    Returns:
        dataset, (X, y): Objeto (Orange.data.Table) com o dataset. O tuplo (X, y) contém
        as features (X) e as classes (y).
    """

    dataset = Orange.data.Table(dataset_path)
    X = dataset.X  # features
    y = dataset.Y  # target/class
    return (dataset, (X, y))

def get_class_name(dataset):
    """
    Obtém os nomes das classes presentes no dataset Orange.

    Args:
        dataset: Dataset carregado com o Orange.

    Returns:
        class_val: Lista com os nomes das classes.
    """

    class_var = dataset.domain.class_var

    class_val = class_var.values
    return class_val
    

def show_train_test_split(X, y, tt_split_indexes, numFirstRows=10 ):
    """
    Mostra um resumo dos índices e dos dados utilizados em cada divisão
    treino/teste.

    Args:
        X: Matriz das features.
        y: Vetor das classes.
        tt_split_indexes: Objeto do Scikit-Learn que trata dos splits.
        numFirstRows: Número de exemplos a mostrar (padrão: 10).
    """

    for ( train_index, test_index ) in tt_split_indexes.split( X, y ):
        print( "summarized data (max = {n:d} instances)".
        format( n=numFirstRows ) )
        train_index = train_index[0:numFirstRows]
        test_index = test_index[0:numFirstRows]
        print( "\n> train-indexes, test-indexes" ) 
        print("train-indexes:", train_index )
        print(" test-indexes:", test_index )
        X_train, y_train = X[train_index], y[train_index]
        X_test, y_test = X[test_index], y[test_index]
        print("\nX_train, y_train" )
        print( X_train, y_train, sep="\n" )
        print("\nX_test, y_test" )
        print( X_test, y_test, sep="\n" )

def show_score(score_all):
    """
    Exibe as métricas de desempenho calculadas de um modelo.

    Args:
        score_all: lista de scores de uma métrica.
    """

    if not score_all: return
    print("::all-evaluated-datasets::")
    
    all_evaluated_datasets = [i*100.0 for i in score_all]
    for v in all_evaluated_datasets: print(" %.2f%% " %(v), end="|")
    if isinstance(score_all, list): score_all = np.array(score_all)
    print("%.2f%% (+/- %.2f%%)" % \
          (score_all.mean()*100.0, score_all.std()*100.0))



def holdout(dataset, test_size, seed=None, p=False):
    (X, y) = dataset

    tt_split_indexes = ShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
    
    if p:
        print("\n=== Holdout ===")
        show_train_test_split(X, y, tt_split_indexes)
    
    return tt_split_indexes

def stratified_holdout(dataset, test_size, seed=None, p=False):
    (X, y) = dataset

    tt_split_indexes = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
    
    if p:
        print("\n=== Stratified Holdout ===")
        show_train_test_split(X, y, tt_split_indexes)
    
    return tt_split_indexes

def repeated_holdout(dataset, test_size, n_repeat, seed=None, p=False):
    (X, y) = dataset

    tt_split_indexes = ShuffleSplit(n_splits=n_repeat, test_size=test_size, random_state=seed)
    
    if p:
        print(f"\n=== Repeated Holdout ({n_repeat} repetitions) ===")
        show_train_test_split(X, y, tt_split_indexes)
    
    return tt_split_indexes

def repeated_stratified_holdout(dataset, test_size, n_repeat, seed=None, p=False):
    (X, y) = dataset

    tt_split_indexes = StratifiedShuffleSplit(n_splits=n_repeat, test_size=test_size, random_state=seed)
    
    if p:
        print(f"\n=== Repeated Stratified Holdout ({n_repeat} repetitions) ===")
        show_train_test_split(X, y, tt_split_indexes)
    
    return tt_split_indexes

def fold_split(dataset, k_folds, seed=None, p=False):
    (X, y) = dataset

    tt_split_indexes = KFold( n_splits=k_folds, shuffle=True, random_state=seed )
    
    if p:
        print(f"\n=== {k_folds}-Fold Cross Validation ===")
        show_train_test_split(X, y, tt_split_indexes)
    
    return tt_split_indexes

def stratified_fold_split(dataset, k_folds, seed=None, p=False):
    (X, y) = dataset

    tt_split_indexes = StratifiedKFold( n_splits=k_folds, shuffle=True, random_state=seed )
    
    if p:
        print(f"\n=== Stratified {k_folds}-Fold Cross Validation ===")
        show_train_test_split(X, y, tt_split_indexes)
    
    return tt_split_indexes

def repeated_fold_split(dataset,  k_folds, n_repeat, seed=None):
    (X, y) = dataset

    tt_split_indexes = RepeatedKFold( n_splits=k_folds, n_repeats=n_repeat, random_state=seed)

    if p:
        print(f"\n=== First {k_folds * n_repeat} splits (first 10 examples each) ===")
        show_train_test_split(X, y, tt_split_indexes)

    return tt_split_indexes

def repeated_stratified_fold_split(dataset, k_folds, n_repeat, seed=None, p=False):
    (X, y) = dataset

    tt_split_indexes = RepeatedStratifiedKFold(n_splits=k_folds, n_repeats=n_repeat, random_state=seed)

    if p:
        print(f"\n=== First {k_folds * n_repeat} splits (first 10 examples each) ===")
        show_train_test_split(X, y, tt_split_indexes)
    
    return tt_split_indexes

def leave_one_out(dataset, p=False):
    (X, y) = dataset

    tt_split_indexes = LeaveOneOut()
    
    if p:
        print("\n=== Leave-One-Out ===")
        show_train_test_split(X, y, tt_split_indexes)
    
    return tt_split_indexes

def leave_p_out(dataset, p_out, p=False):
    (X, y) = dataset

    tt_split_indexes = LeavePOut(p_out)
    
    if p:
        print(f"\n=== Leave-P-Out (P={p_out}) ===")
        show_train_test_split(X, y, tt_split_indexes)
    
    return tt_split_indexes

def bootstrap_split_once(dataset, seed=None, p=False):
    (X, y) = dataset

    tt_split_indexes = MyBootstrapSplitOnce(seed)
    
    if p:
        print("\n=== Bootstrap Split (Once) ===")
        show_train_test_split(X, y, tt_split_indexes)
    
    return tt_split_indexes

def bootstrap_split_repeated(dataset, n_repeat, seed=None, p=False):
    (X, y) = dataset

    tt_split_indexes = MyBootstrapSplitRepeated(n_repeat, seed)
    
    if p:
        print(f"\n=== Bootstrap Split (Repeated {n_repeat} times) ===")
        show_train_test_split(X, y, tt_split_indexes)
    
    return tt_split_indexes


####################
# TESTES 
###################
#dataset = Orange.data.Table("./_datasets/lenses_3RowHeader.tab")
dataset_path = "./_datasets/lenses_3RowHeader.tab"
seed = 10
k_folds = 10
n_repeats = 5
p = 2

(dataset, (X, y)) = orange_to_numpy(dataset_path)
#print(f"Shape X: {X.shape}")
#print(f"Shape y: {y.shape}")



list_func_tt_split = \
[
    #(holdout, (dataset, 1.0/3.0, seed, False)),
    #(stratified_holdout, (dataset, 1.0/3.0, seed, False)),
    #(repeated_holdout, (dataset, 1.0/3.0, n_repeats, seed, False)),
    #(repeated_stratified_holdout, (dataset, 1.0/3.0, n_repeats, seed, False)),
    #(fold_split, (dataset, k_folds, seed, False)),
    #(stratified_fold_split, ((X, y), k_folds, seed, False)),
    #(repeated_fold_split, (dataset, k_folds, n_repeats, seed, False)),
    (repeated_stratified_fold_split, ((X, y), k_folds, n_repeats, seed, False)),
    #(leave_one_out, (dataset, False,)),
    #(leave_p_out, (dataset, p, False)),
    #(bootstrap_split_once, (dataset, seed, False)),
    #(bootstrap_split_repeated, ((X, y), n_repeats, seed, False))
]

list_func_classifier = \
    [
        (OneRule, ()),
        (GaussianNB, ()),
        (DecisionTreeClassifier, ())
    ]

list_score_metric = \
    [
        (accuracy_score, {}),
        (precision_score, {"average":"weighted"}),
        (recall_score, {"average":"weighted"}),
        (f1_score, {"average":"weighted"}),
        (cohen_kappa_score, {})
    ]


####################
# MAIN 
###################
def main():
    fileName = "./_datasets/lenses_3RowHeader.tab"
    dataset, (X, y) = orange_to_numpy(fileName)
    
    class_val = get_class_name(dataset)

    SHOW_CM = False

    print(f"Dataset: {fileName}")
    print(f"Shape X: {X.shape}, \nShape y: {y.shape}")
    print("=" * 60)
    
    for split_idx, (f_tt_split, args_tt_split) in enumerate(list_func_tt_split):
        print(f"\n{split_idx+1}. {f_tt_split.__name__}")
        
        try:
            # Obter os splits
            tt_split_indexes = f_tt_split(*args_tt_split)
            
            # Para cada classificador
            for _, (classifier_func, classifier_args) in enumerate(list_func_classifier):
                print(f"  Classificador: {classifier_func.__name__}")
                
                # Instanciar o classificador
                classifier = classifier_func(*classifier_args)

                # Dicionário para armazenar todos os scores de cada métrica
                all_scores = {metric_func.__name__: [] for metric_func, _ in list_score_metric}

                for split_num, (train_index, test_index) in enumerate(tt_split_indexes.split(X, y)):
                    print(f"    Split {split_num+1}/{tt_split_indexes.get_n_splits() if hasattr(tt_split_indexes, 'get_n_splits') else '?'}")

                    X_train, X_test = X[train_index], X[test_index]
                    y_train, y_test = y[train_index], y[test_index]

                    print("#"*50)
                    print("X (tr/tst):", X_train.shape, X_test.shape)
                    print("y (tr/tst):", y_train.shape, y_test.shape)
                    print("#"*50)
                    
                    y_test_str = y_test.astype(str)
                    
                    # Fit
                    classifier.fit(X_train, y_train)
                    
                    # Predict
                    y_pred = classifier.predict(X_test)
                    
                    y_pred_str = y_pred.astype(str) if hasattr(y_pred, 'astype') else [str(pred) for pred in y_pred]

                    
                    #print("#"*50)
                    ##print(np.unique(y_pred))
                    #print(np.unique(y_test))
                    #print(np.unique(y))
                    #print("#"*50)
                    

                    if SHOW_CM:
                        labels = np.unique(np.concatenate([y_test, y_pred]))
                        cm = confusion_matrix(y_test, y_pred)
                        cm_display = ConfusionMatrixDisplay(
                            confusion_matrix=cm, 
                            display_labels=labels
                        )
                        cm_display.plot(cmap="Blues")
                        plt.title(f"{classifier_func.__name__}")
                        plt.show()


                    # Calcular e armazenar métricas
                    for metric_func, metric_kwargs in list_score_metric:
                        try:
                            score = metric_func(y_test_str, y_pred_str, **metric_kwargs)
                            all_scores[metric_func.__name__].append(score)
                            print(f"      {metric_func.__name__}: {score:.4f}")
                        except Exception as e:
                            print(f"      {metric_func.__name__}: erro - {e}")
                            all_scores[metric_func.__name__].append(0.0)

                # Mostrar estatísticas finais para este classificador
                print("\n" + "="*50)
                print(f"  Resultados finais para {classifier_func.__name__}:")
                print("="*50)
                for metric_name, scores in all_scores.items():
                    if scores and len(scores) > 0:  # se há scores calculados
                        print("\n"+ f">>> {metric_name}:\n")
                        show_score(scores)
                        print("\n")
                    else:
                        print(f"    {metric_name}: Nenhum score calculado")
                
                
                if classifier_func.__name__ == "GaussianNB":
                    dp.save_gaussian_nb_with_pickle(classifier, fileName, class_val)                 
                elif classifier_func.__name__ == "OneRule":
                    dp.save_one_rule_with_pickle(classifier, fileName, class_val)
                elif classifier_func.__name__ == "DecisionTreeClassifier":
                    dp.save_decision_tree_with_pickle(classifier, fileName, class_val)
                    
        except Exception as e:
            print(f">> Erro: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Avaliação completa!")

#_________________________________
if __name__ == "__main__":
    main()