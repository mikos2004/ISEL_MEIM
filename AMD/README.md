
Tiago Alcobia (50521)
Miguel Alcobia (50746)
Fábio Pestana (50756)

---

No caso de querer mudar algo na base de dados:

Para correr o projeto, deve mudar o `psqlPath` no ficheiro `_go.bat` da pasta `scripts`.
Os paths dos ficheiros de export também devem ser modificados no ficheiro `30_script_EXPORT_DATA.txt` para os paths do computador do utilizador.

`XX_script_<Name>.txt`
- `00` → cria a base de dados  
- `01` → cria as tabelas da base de dados  
- `02` → popula a base de dados  
- `03` → cria vistas  
- `30` → exporta os dados  

---

Para correr a versão deployable deve:

Abrir a linha de comandos na pasta `scripts`:

```bash
python deploy_app.py -m <path_do_modelo> -d <path_dos_dados_a_classificar>
```

Em alternativa, também pode alterar a variável `CONFIG` da função `main()` do script `deploy_app.py` e correr o script para usar o programa:

```bash
python deploy_app.py
```

-----

Estrutura:

```bash
scripts
    ├───_datasets				// Pasta com os datasets usados (.tab)
    └───train_result			
        └───models				// modelos treinados e ficheiros json com respetivos metadados
```