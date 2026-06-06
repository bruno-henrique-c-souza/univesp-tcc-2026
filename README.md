# TCC - Análise de Dados de Etanol, Dólar e Petróleo Brent

Este repositório contém os scripts e notebooks para o Trabalho de Conclusão de Curso (TCC) do curso de Ciência de Dados da UNIVESP.

O projeto é dividido em duas etapas principais:
1.  **Tratamento de Dados (`main.py`)**: Processa, limpa e combina séries temporais de preços do Etanol (fonte: Cepea) e do Petróleo Brent.
2.  **Análise e Modelagem (`notebook/llm_xgboost_tcc.ipynb`)**: Utiliza os dados tratados para realizar análises exploratórias e treinar um modelo de previsão com XGBoost.

---

## Etapa 1: Tratamento de Dados com `main.py`

O objetivo do script `main.py` é preparar os dados brutos para a análise.

### 1.1. Pré-requisitos

- Python 3.x instalado.
- As bibliotecas Python necessárias. Você pode instalá-las com o seguinte comando:
  ```bash
  pip install pandas numpy xlrd openpyxl
  ```

### 2. Arquivos de Entrada

Certifique-se de que os seguintes arquivos de dados brutos estejam na mesma pasta que o script `main.py`:

- `cepea-consulta-etanol.xls`: Contém os dados históricos de preço do etanol.
- `petroleo_diario.xls`: Contém os dados históricos de preço do petróleo Brent.
- `Dados_Unificados_TCC_Etanol.xlsx` (Opcional): Se este arquivo já existir, o script irá atualizá-lo com os novos dados processados. Caso contrário, ele será criado.

### 3. Execução

Com o ambiente configurado e os arquivos no lugar, execute o script principal através do terminal:

```bash
python main.py
```

O script irá ler os arquivos de entrada, processar os dados, unir as informações e salvar os resultados.

### 4. Arquivos de Saída

Após a execução, os seguintes arquivos serão gerados ou atualizados no diretório:

- `Dados_Unificados_TCC_Etanol.xlsx`: Contém a série temporal completa, unindo os dados de etanol e petróleo, com tratamento de datas e preenchimento de valores ausentes.
- `Dados_Selecionados_TCC.xlsx`: Uma versão simplificada do arquivo acima, contendo apenas as colunas essenciais (`Date`, `Etanol_Preco`, `Preco_Brent_USD`) para a análise final.
