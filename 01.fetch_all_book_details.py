#OBTÉM DETALHES DOS LIVROS POR URL
import pandas as pd 
import csv
from bs4 import BeautifulSoup
import requests
import re
from time_tracker import track_time
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

def get_links(dataframe:pd.DataFrame)-> list:
    df= dataframe
    book_urls = set(df['book_url'].dropna())
    return list(book_urls)
    
# MÉTODO DEVOLVE HTML DA URL 
def fetch_page(url: str):
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1'
    }
    proxies = {
        'http': 'socks5h://127.0.0.1:9050',  # Configuração para HTTP via Tor
        'https': 'socks5h://127.0.0.1:9050'  # Configuração para HTTPS via Tor
    }
    try:
        for attempt in range(5):
            wait_time = 0.1
            print(f"Connecting to URL: {url}\n")
            time.sleep(wait_time)  # Adiciona o atraso antes de cada requisição
            response = requests.get(url, headers=headers,proxies=proxies, timeout=(60, 60))
            if response.status_code in (429,443) :
                wait_time = random.uniform(15, 30)  # Espera mais em caso de "429"
                print(f"Too many requests. Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
                continue
            response.raise_for_status()
            return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error acessing page: {e}")
        return None

def parse_page(html):
    # Inicializar variáveis
    books = []

    # Parsear o HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Procurar os detalhes do produto
    product_panels = soup.find_all('div', class_='painel-lateral')
    product_details_list = soup.find_all('div', class_='sinopse')
    
    for product_panel, product_details in zip(product_panels, product_details_list):
        book_id = None
        sinopse = None

        try:
            if product_panel and product_details:
                # Extrai os dados básicos do produto
                book_name = product_panel.find('div', class_='product-name').get_text(strip=True)
                book_author = product_panel.find('div', class_='author').get_text(strip=True)
                book_id = f"{book_name} - {book_author}"

                # Extrair a sinopse antes da "Ficha Técnica"
                sinopse_div = product_details.find('div')
                if sinopse_div:
                    sinopse_paragraphs = sinopse_div.find_all('p')
                    sinopse = " ".join([p.get_text(strip=True) for p in sinopse_paragraphs])  # Junta os parágrafos

                # Procurar "Ficha Técnica" de forma flexível
                ficha_tecnica = soup.find_all(string=lambda text: "Ficha Técnica" in text)

                if ficha_tecnica:
                    ficha_dict = {}
                    for item in ficha_tecnica:
                        # Procurar todos os elementos subsequentes após "Ficha Técnica"
                        next_elements = item.find_all_next(string=True)
                        for element in next_elements:
                            text = element.strip()
                            # Ignorar strings vazias
                            if not text:
                                continue
                            # Verificar se alcançamos o fim dos dados relevantes
                            if "//<![CDATA" in text:
                                break
                            # Procurar chave e valor
                            if ":" in text:
                                chave, valor = text.split(":", 1)
                                ficha_dict[chave.strip()] = valor.strip()

                    book = {
                        'book_id': book_id,
                        'sinopse': sinopse,
                        'ean': ficha_dict.get('EAN'),
                        'editora': ficha_dict.get('Fabricante', ficha_dict.get('Editora')),
                        'paginas': ficha_dict.get('Páginas', ficha_dict.get('Número de Páginas')),
                        'idioma': ficha_dict.get('Idioma'),
                        'isbn': ficha_dict.get('ISBN'),
                        'idade_minima': ficha_dict.get('Idade mínima')
                    }
                    books.append(book)
                else:
                    print(f"Ficha Técnica não encontrada para o livro: {book_name}")
        except AttributeError as e:
            print(f"Erro ao processar o produto: {e}")

    return books


# MÉTODO PARA SALVAR EM CSV
def save_to_csv(books, filename):
    if books:
        keys = books[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=keys, delimiter=';', quotechar='"')
            writer.writeheader()
            writer.writerows(books)

if __name__ == "__main__":
    start_time = time.time()
    #file = 'data/livros_raw.csv'
    file = 'data/remains_url.csv'
    all_books = []
    
    # Carregar as URLs e preparar o lote
    urls = pd.read_csv(file, sep=';', quotechar='"')
    urls_unique = get_links(urls)
    
    urls_sample = urls_unique  # Seleciona as URLs de interesse

    # Processar URLs em lotes
    for i in range(0, len(urls_sample), 3):  # Dividir URLs em lotes de 3
        start_url_time = time.time()
        batch = urls_sample[i:i+3]
        
        # Usar ThreadPoolExecutor para processar o lote atual
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_url = {executor.submit(fetch_page, url): url for url in batch}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    html = future.result()
                    if html:
                        books = parse_page(html)
                        all_books.extend(books)
                except Exception as e:
                    print(f"Erro ao processar a URL {url}: {e}")
        elapsed_time = time.time() - start_url_time
        print(f"Batch collected in {elapsed_time:.2f} seconds\n")
        # Pausa entre os lotes
        time.sleep(random.uniform(0.5, 1))
    

    if all_books:
        # save_to_csv(all_books, '02-livros_detalhes_raw.csv')
        save_to_csv(all_books, 'livros_detalhes_raw_remains.csv')

    # Calcula e exibe o tempo total
    end_time = time.time()
    elapsed_time = (end_time - start_time)
    minutes = int(elapsed_time // 60)
    seconds = elapsed_time % 60
    print(f"\nProcesso concluído em {minutes} min. {seconds:.2f} seconds")
        

# if __name__=="__main__":
#     start_time = time.time()
#     file = 'livros_senso_incomum_bruto.csv'
#     all_books=[]
    
#     urls = pd.read_csv(file, sep=';', quotechar='"')
#     urls_unique = get_links(urls)
#     urls_sorted = urls.sort_values(by='book_url', ascending=True)
#     urls_unique = get_links(urls_sorted)
#     urls_sample = urls_unique[4001:]
    
#     for url in urls_sample:
#         start_time2 = time.time()
#         html = fetch_page(url)
#         if html:
#             books = parse_page(html)
#             all_books.extend(books)
#             elapsed_time = time.time() - start_time2
#             print(f"Link collected in {elapsed_time:.2f} seconds\n")
    
#     if all_books:
#         save_to_csv(all_books, 'detalhes_livros_coletados_senso_incomum_first_4001-max.csv')
#     # Calcula e exibe o tempo total
#     end_time = time.time()  # Marca o tempo final
#     elapsed_time = (end_time - start_time) / 60  # Calcula o tempo em minutos
#     print(f"\n Processo concluído em {elapsed_time:.2f} minutos.")