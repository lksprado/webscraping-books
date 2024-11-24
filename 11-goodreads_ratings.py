import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd 
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def fetch_page(isbn, max_retries=3, wait_time=10):
    """
    Busca a página do Goodreads para um ISBN específico, com lógica de repetição em caso de falha.
    """
    url = f'https://www.goodreads.com/search?q={isbn}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 429:  # Too Many Requests
                print(f"Too Many Requests. Aguardando {wait_time} segundos antes de tentar novamente...")
                time.sleep(wait_time)
                retries += 1
                continue
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar a página para ISBN {isbn}: {e}")
            retries += 1
            time.sleep(wait_time)

    print(f"Falha ao obter a página para ISBN {isbn} após {max_retries} tentativas.")
    return None


def get_isbn(dataframe: pd.DataFrame):
    """Extrai os ISBNs únicos, excluindo valores nulos."""
    df = dataframe
    df = df['isbn'].dropna().drop_duplicates()
    return df.tolist()

def extract_book_data(html):
    soup = bs(html, 'html.parser')
    
    # Inicializa os valores com "N/A" como padrão
    rating_value, rating_count, review_count, publication_year = 'N/A', 'N/A', 'N/A', 'N/A'

    # Localiza o script do tipo application/ld+json
    script_tag = soup.find('script', {'type': 'application/ld+json'})
    if script_tag:
        try:
            book_data = json.loads(script_tag.string)
            aggregate_rating = book_data.get('aggregateRating', {})
            rating_value = aggregate_rating.get('ratingValue', 'N/A')
            rating_count = aggregate_rating.get('ratingCount', 'N/A')
            review_count = aggregate_rating.get('reviewCount', 'N/A')
        except json.JSONDecodeError:
            print("Erro ao decodificar o JSON.")

    # Extrai a informação de publicação
    publication_info_tag = soup.find('p', {'data-testid': 'publicationInfo'})
    if publication_info_tag:
        publication_text = publication_info_tag.get_text(strip=True)
        if "published" in publication_text.lower():
            try:
                publication_year = publication_text.split()[-1]
                if not publication_year.isdigit() or len(publication_year) != 4:
                    publication_year = 'N/A'
            except IndexError:
                publication_year = 'N/A'
    
    return rating_value, rating_count, review_count, publication_year

def save_to_csv_with_pandas(data, filename='good_reads_detail_v2.csv'):
    # Converte os dados em um DataFrame
    df_new = pd.DataFrame(data, columns=['isbn', 'rating_value', 'rating_count', 'review_count', 'publication_year'])
    
    # Salva diretamente no modo 'append' para evitar leitura e concatenação
    df_new.to_csv(filename, index=False, sep=";", quotechar='"', mode='a', header=not pd.io.common.file_exists(filename))

def process_isbn(isbn, counter):
    isbn_start_time = time.time()
    html = fetch_page(isbn)
    if html:
        rating_value, rating_count, review_count, publication_year = extract_book_data(html)
    else:
        print(f"Falha ao obter dados para ISBN {isbn}.")
        rating_value, rating_count, review_count, publication_year = None, None, None, None
    isbn_end_time = time.time()
    elapsed_time = isbn_end_time - isbn_start_time
    print(f"{counter} - Dados extraídos para ISBN {isbn} em {elapsed_time:.2f} segundos.")
    return (counter, isbn, rating_value, rating_count, review_count, publication_year)

if __name__ == "__main__":
    try:
        # Lista de ISBNs a serem consultados
        input_file = 'data/04-final_books.csv'
        df = pd.read_csv(input_file, sep=";", encoding='utf-8', quotechar='"')

        isbn_ls = get_isbn(df)
        data = {}

        # Usa ThreadPoolExecutor para processar 3 requisições simultaneamente
        with ThreadPoolExecutor(max_workers=3) as executor:
            script_start_time = time.time()
            futures = []
            counter = 1  # Inicializa o contador
            for isbn in isbn_ls:
                futures.append(executor.submit(process_isbn, isbn, counter))
                counter += 1
                # Pausa de 0,2 segundos a cada submissão
                if len(futures) % 3 == 0:
                    time.sleep(0.2)

            for future in as_completed(futures):
                counter, isbn, rating_value, rating_count, review_count, publication_year = future.result()
                data[counter] = (isbn, rating_value, rating_count, review_count, publication_year)

        # Ordena os resultados pelo contador (que garante a ordem correta)
        sorted_data = [data[key] for key in sorted(data.keys())]

        # Salva os dados no CSV ao término do processamento
        save_to_csv_with_pandas(sorted_data)

        script_end_time = time.time()
        elapsed_time = (script_end_time - script_start_time)
        minutes = int(elapsed_time // 60)
        seconds = elapsed_time % 60
        print(f"\nProcesso concluído em {minutes} min. {seconds:.2f} seconds")

    except Exception as e:
        print(f"Erro inesperado: {e}")