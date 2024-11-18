# OBTEM OS LINKS CATEGORIAS



import requests
from bs4 import BeautifulSoup

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

# def parse_page(html):
#     soup = BeautifulSoup(html, 'html.parser')
#     return soup.prettify()

def parse_pages(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    
    # Encontra todos os elementos <li> com a classe 'with-child'
    page_items = soup.find_all('div', class_='links')
    
    for link_div in page_items:
        # Encontra o link principal da categoria
        page_links = link_div.find_all('a', href=True)
        for page_link in page_links:
            links.append(page_link['href'])
                
    return links

# Teste das funções
if __name__ == '__main__':
    page_content = fetch_page()
    
    if page_content:
        category_links = parse_pages(page_content)
        print("Links encontrados em 'category-aditional':")
        for link in category_links:
            print(link)
    else:
        print("Falha ao obter o HTML da página.")