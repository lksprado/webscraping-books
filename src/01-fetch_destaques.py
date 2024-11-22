# OBTEM OS LINKS DESTACADOS NO CABEÇALHO

import requests
from bs4 import BeautifulSoup

def fetch_page():
    url = 'https://livraria.sensoincomum.org/'
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

def parse_main_categories(html):
    soup = BeautifulSoup(html, 'html.parser')
    pages = set()
    
    # Encontra o div com a classe 'category-aditional'
    links = soup.find('div', class_='category-aditional')
    
    for link in links.find_all('a', href=True):
        if 'href' in link.attrs:
            if link.attrs['href'] not in pages:
                newPage = link.attrs['href']
                pages.add(newPage)
    return pages

if __name__ == '__main__':
    page_content = fetch_page()
    
    if page_content:
        category_links = parse_main_categories(page_content)
        print("Links encontrados nos destaques:\n")
        for link in category_links:
            print(link)
    else:
        print("Falha ao obter o HTML da página.")
