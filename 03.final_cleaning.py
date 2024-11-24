# CRIA BASE BASE FINAL TRATADA
import pandas as pd 
import numpy as np


def concat_details(file1:str, file2:str):
    """junta os dataframes de detalhes de livros primeira passada e a retentativa"""
    df1 = pd.read_csv(file1, encoding='utf-8', sep=';', quotechar='"')
    df2 = pd.read_csv(file2, encoding='utf-8', sep=';', quotechar='"')
    df3 = pd.concat([df1,df2], ignore_index=True)
    df3 = df3.drop_duplicates()
    return df3

def join_book_details_to_main(dataframe_main: pd.DataFrame, dataframe_detail: pd.DataFrame):
    df = dataframe_main.merge(dataframe_detail, how='left', on='book_id')
    return df


def final_cleaning(dataframe: pd.DataFrame):
    df = dataframe
    df = df.drop_duplicates()

    df.loc[:, 'book_price_old'] = df['book_price_old'].str.replace('R$ ', '').str.replace('.','').str.replace(',','.').astype('Float64')
    df.loc[:, 'book_price_new'] = df['book_price_new'].str.replace('.','').str.replace(',','.').astype('Float64')
    df['book_discount'] = ((df['book_price_new'] - df['book_price_old']) / 100).round(2)
    df['book_discount'] = df['book_discount'].apply(lambda x: f"{x:.2f}")
    df.loc[:, 'paginas'] = df['paginas'].replace(0.0, np.nan).astype('Int64')
    df.loc[:, 'idade_minima'] = df['idade_minima'].astype('Int64')
    df.loc[:, 'isbn'] = df['isbn'].fillna("").astype(str).str.replace('-', '', regex=False).str.replace('.', '', regex=False).str.replace('x', 'X', regex=False).str.replace('*', '', regex=False)
    df.loc[:, 'ean'] = df['ean'].fillna("").astype(str).str.replace('-', '', regex=False).str.replace('.0', '', regex=False)



    
    # Selecionar colunas específicas
    df = df[['time', 'sinopse', 'book_name', 'book_author', 'book_category',
            'book_price_new', 'book_discount', 'book_price_old', 'paginas',
            'editora', 'idade_minima', 'isbn', 'ean', 'idioma', 'book_url', 'book_id']]

    return df

if __name__=="__main__":
    books_raw = 'data/00-livros_raw.csv'
    df_books_raw = pd.read_csv(books_raw, encoding='utf-8', sep=';', quotechar='"')
    
    books_details = 'data/01-livros_detalhes_raw.csv'
    books_details_remains = 'data/03-livros_detalhes_raw_remains.csv'
    df_details = concat_details(books_details, books_details_remains)
    
    df_joined = join_book_details_to_main(df_books_raw, df_details)
    
    df_final = final_cleaning(df_joined)
    
    df_final.to_csv('data/04-final_books.csv', encoding='utf-8', sep=';', quotechar='"', index=False)
    
    