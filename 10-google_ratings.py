import pandas as pd
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_isbn(dataframe: pd.DataFrame):
    """Extrai os ISBNs únicos, excluindo valores nulos."""
    df = dataframe
    df = df['isbn'].dropna().drop_duplicates()
    return df.tolist()

def fetch_googlebooks(isbn, retries=3):
    """Realiza uma requisição com tentativas de repetição em caso de falha."""
    for attempt in range(retries):
        try:
            response = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}')
            if response.status_code == 200:
                result = response.json()
                if result.get("totalItems", 0) == 1:
                    volume_info = result["items"][0].get("volumeInfo", {})
                    print(f"ISBN {isbn} collected successfully")
                    return {
                        "isbn": isbn,
                        "page_count": volume_info.get("pageCount", None),
                        "rating_value": volume_info.get("averageRating", None),
                        "rating_count": volume_info.get("ratingsCount", None),
                        "published_date": volume_info.get("publishedDate", None),
                    }
                else:
                    print(f"No details found for ISBN {isbn}")
                    return None
            elif response.status_code == 429:
                print(f"Rate limit exceeded for ISBN {isbn}, retrying... ({attempt + 1}/{retries})")
                time.sleep(1)  # Aguarda 1 segundos
            else:
                print(f"Request failed for ISBN {isbn}: Status code {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching data for ISBN {isbn}: {e}")
            return None
    return None  # Falhou após todas as tentativas

def get_googlebooks_concurrent(isbn_list: list, output_file: str, max_workers: int = 5):
    """Faz requisições simultâneas à API do Google Books, com lotes de ISBNs."""
    data = []
    batch_start_time = time.time()  # Marca o início do lote

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Envia tarefas para execução simultânea
        future_to_isbn = {executor.submit(fetch_googlebooks, isbn): isbn for isbn in isbn_list}
        
        for future in as_completed(future_to_isbn):
            isbn = future_to_isbn[future]
            try:
                result = future.result()
                if result:  # Adiciona resultados válidos
                    data.append(result)
            except Exception as e:
                print(f"An error occurred while processing ISBN {isbn}: {e}")

    # Registra o tempo total do lote
    batch_elapsed_time = time.time() - batch_start_time
    print(f"Batch collected in {batch_elapsed_time:.2f} seconds")
    
    # Cria o DataFrame com os dados coletados
    df = pd.DataFrame(data)
    df.to_csv(output_file, sep=";", index=False)
    print(f"Results saved to {output_file}")
    return df

if __name__ == "__main__":
    input_file = 'data/04-final_books.csv'
    output_file = 'googleapi_details.csv'
    
    df = pd.read_csv(input_file, sep=";", encoding='utf-8', quotechar='"')
    df_isbn = get_isbn(df)

    result_df = get_googlebooks_concurrent(df_isbn, output_file, max_workers=3)
    print("Execution completed successfully!")
