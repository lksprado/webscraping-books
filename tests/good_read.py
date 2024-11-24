import requests
from bs4 import BeautifulSoup as bs
import json


#response = requests.get(f'https://www.goodreads.com/search?q={isbn}')
#https://www.goodreads.com/search?q=9788567801216

def fetch_page():
    url = 'https://www.goodreads.com/search?q=9788545200567'
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
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Garante que a resposta foi bem-sucedida
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a página: {e}")
        return None
    

def extract_book_data(html):
    soup = bs(html, 'html.parser')
    
    # Localiza o script do tipo application/ld+json para as classificações
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
    else:
        rating_value, rating_count, review_count = 'N/A', 'N/A', 'N/A'
    
    # Extrai a informação de publicação
    publication_info_tag = soup.find('p', {'data-testid': 'publicationInfo'})
    if publication_info_tag:
        publication_text = publication_info_tag.get_text(strip=True)
        # Exemplo de texto: "First published January 1, 1912"
        if "published" in publication_text.lower():
            # Extrai o ano de publicação
            publication_year = publication_text.split(" ")[-1]
        else:
            publication_year = 'N/A'
    else:
        publication_year = 'N/A'
    
    return rating_value, rating_count, review_count, publication_year

if __name__ == "__main__":
    html = fetch_page()
    if html:
        book_info = extract_book_data(html)
        if book_info:
            print(book_info)
        else:
            print("Dados do livro não encontrados.")
