import pandas as pd 
import numpy as np

file_main = 'data/04-final_books.csv'
file_google = 'data/googleapi_details.csv'
file_goodreads = 'data/good_reads_detail_v2.csv'

df_main = pd.read_csv(file_main, sep=';', encoding='utf-8', quotechar='"')
df_google = pd.read_csv(file_google, sep=';', encoding='utf-8', quotechar='"')
df_goodreads = pd.read_csv(file_goodreads, sep=';', encoding='utf-8', quotechar='"')


df_google['published_date'] = df_google['published_date'].str[:4]
df_google['page_count'] = df_google['page_count'].replace(0.0, np.nan)
df_google = df_google.dropna(subset=['page_count', 'rating_value', 'rating_count','published_date'], how='all') 

df_goodreads = df_goodreads.dropna(subset=['rating_value', 'rating_count', 'review_count','publication_year'], how='all') 

df_details_join = df_google.merge(df_goodreads, how='outer', on='isbn', suffixes=('_google', '_goodreads')) 
df_details_join['rating_value'] = df_details_join['rating_value_goodreads'].fillna(df_details_join['rating_value_google'])
df_details_join['rating_count'] = df_details_join['rating_count_goodreads'].fillna(df_details_join['rating_count_google'])
df_details_join['year'] = df_details_join['publication_year'].fillna(df_details_join['published_date'])

df_details_join['year'] = pd.to_numeric(df_details_join['year'], errors='coerce')
df_details_join['year'] = df_details_join['year'].astype('Int64')
df_details_join['rating_count'] = df_details_join['rating_count'].astype('Int64')
df_details_join['review_count'] = df_details_join['review_count'].astype('Int64')
df_details_join['rating_value'] = round(df_details_join['rating_value'].astype('Float64'),1)
df_details_join['page_count'] = df_details_join['page_count'].astype('Int64')


df_details_join.drop(columns=['rating_value_goodreads', 'rating_value_google', 'rating_count_goodreads', 'rating_count_google', 'published_date', 'publication_year'], inplace=True)

df_final = df_main.merge(df_details_join, how='left', on='isbn')

df_final['paginas'] = df_final['paginas'].fillna(df_details_join['page_count'])
df_final.drop(columns=['page_count'])

df_final.to_csv('data/final_books_details.csv', sep=';', quotechar='"', encoding='utf-8', index=False)