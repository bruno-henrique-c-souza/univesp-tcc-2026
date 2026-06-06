import pandas as pd
import numpy as np
import os

# --- Configuração dos Nomes dos Arquivos ---
# Arquivo de origem com dados históricos do etanol
arquivo_etanol = 'cepea-consulta-etanol.xls'
# Arquivo de origem com dados históricos do petróleo
arquivo_petroleo = 'petroleo_diario.xls'
# Arquivo adicional com os registros de 03-2021 até 04-2026
arquivo_alvo = 'Dados_Unificados_TCC_Etanol.xlsx'
# Arquivo final que conterá apenas as colunas selecionadas
arquivo_final_selecionado = 'Dados_Selecionados_TCC.xlsx'

# Anos para filtrar para não conflitar com os dados unificados
ano_inicio = 2016
ano_fim = 2020

# --- Colunas para o arquivo final ---
colunas_para_manter = ['Date', 'Etanol_Preco', 'Preco_Brent_USD']

def processar_dados_etanol(caminho_arquivo, ano_inicio, ano_fim):
    """
    Carrega e processa os dados de etanol do Cepea, filtrando por ano e selecionando colunas.
    """
    print(f"Processando arquivo de etanol: {caminho_arquivo}...")
    try:
        # Lê o arquivo .xls
        # Arquivos do Cepea frequentemente têm cabeçalhos extras, por isso 'skiprows=3'.
        # Ajuste o valor de 'skiprows' se o formato do seu arquivo for diferente.
        df = pd.read_excel(caminho_arquivo, engine='xlrd', skiprows=3)

        # Seleciona apenas as duas primeiras colunas e as renomeia.
        df = df.iloc[:, :2].copy()
        df.columns = ['Data', 'Valor']

        # Converte a coluna de data para o formato datetime.
        # 'errors='coerce'' transformará datas inválidas em NaT (Not a Time).
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce', dayfirst=True)

        # Remove linhas onde a data não pôde ser convertida.
        df.dropna(subset=['Data'], inplace=True)

        # O método 'ffill' (forward fill) repete o valor de sexta-feira para o sábado e domingo.
        # df['Valor'] = df['Valor'].ffill()

        # Filtra os dados pelo intervalo de anos especificado.
        filtro_ano = (df['Data'].dt.year >= ano_inicio) & (df['Data'].dt.year <= ano_fim)
        df_filtrado = df[filtro_ano].copy()

        # Renomeia as colunas para o nome final desejado no arquivo de destino.
        df_filtrado.rename(columns={'Data': 'Date', 'Valor': 'Etanol_Preco'}, inplace=True)

        print(f"  -> {len(df_filtrado)} registros de etanol encontrados entre {ano_inicio} e {ano_fim}.")
        return df_filtrado[['Date', 'Etanol_Preco']]

    except FileNotFoundError:
        print(f"ERRO: Arquivo de etanol não encontrado em '{caminho_arquivo}'.")
        return pd.DataFrame(columns=['Date', 'Etanol_Preco'])
    except Exception as e:
        print(f"ERRO ao processar o arquivo de etanol: {e}")
        return pd.DataFrame(columns=['Date', 'Etanol_Preco'])


def processar_dados_petroleo(caminho_arquivo, ano_inicio, ano_fim):
    """
    Carrega e processa os dados diários de petróleo, filtrando por ano e selecionando colunas.
    """
    print(f"Processando arquivo de petróleo: {caminho_arquivo}...")
    try:
        # Lê o arquivo .xls.
        df = pd.read_excel(caminho_arquivo, engine='xlrd')

        # Renomeia as colunas para o padrão desejado.
        df.rename(columns={'Data': 'Date', 'Preço': 'Preco_Brent_USD'}, inplace=True)

        # Verifica se as colunas esperadas existem após a renomeação.
        if 'Date' not in df.columns or 'Preco_Brent_USD' not in df.columns:
            raise ValueError("Colunas 'Data' e/ou 'Preço' não encontradas no arquivo de petróleo.")

        # Converte a coluna de data para o formato datetime.
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce', dayfirst=True)
        df.dropna(subset=['Date'], inplace=True)

        # Filtra os dados pelo intervalo de anos.
        filtro_ano = (df['Date'].dt.year >= ano_inicio) & (df['Date'].dt.year <= ano_fim)
        df_filtrado = df[filtro_ano].copy()

        print(f"  -> {len(df_filtrado)} registros de petróleo encontrados entre {ano_inicio} e {ano_fim}.")
        return df_filtrado[['Date', 'Preco_Brent_USD']]

    except FileNotFoundError:
        print(f"ERRO: Arquivo de petróleo não encontrado em '{caminho_arquivo}'.")
        return pd.DataFrame(columns=['Date', 'Preco_Brent_USD'])
    except Exception as e:
        print(f"ERRO ao processar o arquivo de petróleo: {e}")
        return pd.DataFrame(columns=['Date', 'Preco_Brent_USD'])


def unir_e_salvar_dados(arquivo_alvo, df_etanol, df_petroleo):
    """
    Une os dataframes de etanol e petróleo a um arquivo alvo.
    Se o arquivo alvo existir, ele será atualizado. Caso contrário, será criado.
    """
    # Une os dois dataframes de origem em um só, usando a data como chave.
    # A junção 'outer' garante que todas as datas de ambos os arquivos sejam mantidas.
    df_fontes_unidas = pd.merge(df_etanol, df_petroleo, on='Date', how='outer')

    df_alvo = None
    if os.path.exists(arquivo_alvo):
        print(f"Carregando arquivo de destino existente: {arquivo_alvo}")
        try:
            df_alvo = pd.read_excel(arquivo_alvo, engine='openpyxl')
            # Garante que a coluna 'Date' do alvo seja do tipo datetime.
            if 'Date' in df_alvo.columns:
                df_alvo['Date'] = pd.to_datetime(df_alvo['Date'], errors='coerce')
            else:
                # Se o arquivo alvo não tiver uma coluna 'Date', tratamos como um arquivo novo.
                print("AVISO: Arquivo alvo não possui coluna 'Date'. Os dados serão combinados.")
                df_alvo = None
        except Exception as e:
            print(f"ERRO ao ler o arquivo de destino '{arquivo_alvo}': {e}. Um novo arquivo será criado.")
            df_alvo = None

    if df_alvo is None or df_alvo.empty:
        print("Criando novo dataframe de destino com os dados de origem.")
        df_final = df_fontes_unidas
    else:
        print("Unindo dados de origem ao dataframe de destino...")
        # A estratégia é usar a data como um índice para atualizar e combinar os dados.
        df_alvo.set_index('Date', inplace=True)
        df_fontes_unidas.set_index('Date', inplace=True)

        # Garante que as colunas de destino existam no dataframe alvo.
        if 'Etanol_Preco' not in df_alvo.columns:
            df_alvo['Etanol_Preco'] = np.nan
        if 'Preco_Brent_USD' not in df_alvo.columns:
            df_alvo['Preco_Brent_USD'] = np.nan
            
        # O método update atualiza o df_alvo com os dados de df_fontes_unidas,
        # sobrescrevendo valores existentes e preenchendo os que faltam.
        df_alvo.update(df_fontes_unidas)

        # Combina os índices para incluir datas que possam existir nas fontes mas não no alvo.
        indice_combinado = df_alvo.index.union(df_fontes_unidas.index)
        df_final = df_alvo.reindex(indice_combinado)

        # Reseta o índice para que 'Date' volte a ser uma coluna.
        df_final.reset_index(inplace=True)

    # Ordena o dataframe final pela data e remove linhas duplicadas, se houver.
    df_final.sort_values(by='Date', inplace=True)
    df_final.drop_duplicates(subset=['Date'], keep='last', inplace=True)

    # O método 'ffill' (forward fill) repete o valor de sexta-feira para o sábado e domingo.
    df_final['Etanol_Preco'] = df_final['Etanol_Preco'].ffill()

    # Remove as linhas onde o 'Etanol_Preco' ainda está em branco (NaN) após o ffill.
    # Isso geralmente acontece no início do período se os primeiros dias não tiverem dados.
    linhas_antes = len(df_final)
    df_final.dropna(subset=['Etanol_Preco'], inplace=True)
    print(f"Removendo linhas com Etanol_Preco em branco. Linhas removidas: {linhas_antes - len(df_final)}")

    # Salva o dataframe final no arquivo Excel.
    try:
        print(f"Salvando dados unificados em '{arquivo_alvo}'...")
        df_final.to_excel(arquivo_alvo, index=False, engine='openpyxl')
        print("Processo concluído com sucesso!")
    except Exception as e:
        print(f"ERRO ao salvar o arquivo final: {e}")


def selecionar_colunas_e_salvar(arquivo_origem, arquivo_destino, colunas_selecionadas):
    """
    Lê um arquivo Excel de origem, seleciona colunas específicas e salva em um novo arquivo.
    """
    print("\n--- Iniciando a seleção de colunas para o arquivo final ---")
    try:
        if not os.path.exists(arquivo_origem):
            print(f"ERRO: O arquivo de origem '{arquivo_origem}' não foi encontrado. Esta etapa será pulada.")
            return

        print(f"Lendo arquivo de origem: {arquivo_origem}")
        df = pd.read_excel(arquivo_origem, engine='openpyxl')

        # Verifica quais das colunas desejadas realmente existem no dataframe
        colunas_existentes = [col for col in colunas_selecionadas if col in df.columns]
        colunas_faltantes = set(colunas_selecionadas) - set(colunas_existentes)

        if colunas_faltantes:
            print(f"AVISO: As seguintes colunas não foram encontradas e não serão incluídas: {list(colunas_faltantes)}")

        if not colunas_existentes:
            print("ERRO: Nenhuma das colunas selecionadas foi encontrada. O arquivo final não será gerado.")
            return

        df_selecionado = df[colunas_existentes]

        print(f"Salvando colunas {colunas_existentes} em '{arquivo_destino}'...")
        df_selecionado.to_excel(arquivo_destino, index=False, engine='openpyxl')
        print("Arquivo com colunas selecionadas salvo com sucesso!")

    except Exception as e:
        print(f"ERRO ao selecionar colunas e salvar o arquivo: {e}")


# --- Execução Principal do Script ---
if __name__ == "__main__":
    # 1. Processa os arquivos de origem para extrair e filtrar os dados.
    dados_etanol = processar_dados_etanol(arquivo_etanol, ano_inicio, ano_fim)
    dados_petroleo = processar_dados_petroleo(arquivo_petroleo, ano_inicio, ano_fim)

    # 2. Procede para a união apenas se algum dado tiver sido carregado.
    if not dados_etanol.empty or not dados_petroleo.empty:
        unir_e_salvar_dados(arquivo_alvo, dados_etanol, dados_petroleo)

        # 3. Após unir, seleciona as colunas principais e salva em um novo arquivo.
        #    Usa o 'arquivo_alvo' como origem para esta etapa.
        selecionar_colunas_e_salvar(arquivo_alvo, arquivo_final_selecionado, colunas_para_manter)
    else:
        print("Nenhum dado foi carregado dos arquivos de origem. O arquivo de destino não foi modificado.")
