# OBTEM OS LINKS CATEGORIAS



import requests
from bs4 import BeautifulSoup
import re

def fetch_page():
    url = 'https://livraria.sensoincomum.org/filosofia'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a página: {e}")
        return None

def parse_pages(html):
    soup = BeautifulSoup(html, 'html.parser')
    pages = set()
    regex = r"(?<=\?page=)\d+"
    
    # Encontra todos os elementos <li> com a classe 'with-child'
    page_items = soup.find_all('div', class_='links')
    
    for link_div in page_items:
        # Encontra o link principal da categoria
        page_links = link_div.find_all('a', href=True)
        for page_link in page_links:
            href = page_link['href']
            # Procura por números após '?page='
            match = re.search(regex, href)
            if match:
                # Adiciona o número da página ao conjunto
                pages.add(int(match.group()))
    if pages:
        full_range = set(range(min(pages), max(pages) + 1))
        pages.update(full_range)
    return pages

# Teste das funções
if __name__ == '__main__':
    page_content = fetch_page()
    
    if page_content:
        category_links = parse_pages(page_content)
        print("Páginas encontradas:\n")
        for link in category_links:
            print(link)
    else:
        print("Falha ao obter o HTML da página.")