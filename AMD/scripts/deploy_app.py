# Tiago Alcobia - 50521
# Miguel Alcobia - 50746
# Fábio Pestana - 50756

# Upload do modelo
# Upload dos dados a classificar
# Predict dos dados
# Guardar resultado num txt

import os
import sys

import numpy as np
import aux_data_preparation as dp
import aux_split_eval as spev
import e_Config_app as config

def main():
    CONFIG = True

    if CONFIG:
        cfg = config.e_Config()
        cfg.config(sys.argv)
        
        model_path = cfg.get_model_path()
        data_path = cfg.get_data_path()

        print(f"Modelo: {model_path}")
        print(f"Dados: {data_path}")
        
        classifier = dp.load_model_with_pickle(model_path)

        json_file = os.path.splitext(model_path)[0]
        json_path = json_file+".json"

        _, (X, _) = spev.orange_to_numpy(data_path)

    else:
        print("Qual o modelo treinado que pretende utilizar? \nPath:")
        model_path = input()
        classifier = dp.load_model_with_pickle(model_path)

        json_file = os.path.splitext(model_path)[0]
        json_path = json_file+".json"

        print("\nQual o path dos dados (.tab) que pretende classificar? \nPath:")
        data_path = input()
        _, (X, _) = spev.orange_to_numpy(data_path)


    y_pred = classifier.predict(X)

    #print(y_pred)

    for i in range(len(y_pred)):
        #print("TYPE", type(i))
        class_pred = dp.get_class_name_idx(
            idx = int(float(y_pred[i])), 
            json_path= json_path
        )
                                           
        print(f"Resultado {i}:", class_pred)


#_________________________________
if __name__ == "__main__":
    main()