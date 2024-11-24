# OBTÉM LISTA DE DETALHES FALTANTES PARA RETENTATIVA

import pandas as pd 


def join(df1: pd.DataFrame ,df2: pd.DataFrame):
    df = pd.read_csv(df1, sep=';', quotechar='"', encoding ='utf-8')
    df_final = df.merge(df2, how='left', on='book_id')
    return df_final

def clean(dataframe:pd.DataFrame):
    df = dataframe
    filtro = pd.isna(df['paginas'])
    df = df.loc[filtro,['book_url']]
    df = df.drop_duplicates()
    return df
    

if __name__=="__main__":
    file_details = 'data/livros_detalhes_raw.csv'
    file_raw = 'data/livros_raw.csv'
    
    dfs = pd.read_csv(file_details, sep=';', quotechar='"', encoding='utf-8') 
    df_first_join = join(file_raw, dfs)
    
    # BOOK_URL que faltaram informacao no primeiro scrap
    df_remains = clean(df_first_join)
    df_remains.to_csv('data/remains_url.csv', sep=';', encoding='utf-8', quotechar='"', index=False)