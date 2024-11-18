# OBTEM OS LINKS CATEGORIAS



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

# def parse_page(html):
#     soup = BeautifulSoup(html, 'html.parser')
#     return soup.prettify()

def parse_category_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    
    # Encontra todos os links dentro de <li> que contêm a classe 'category'
    category_items = soup.find_all('li', class_=['', 'with-child'])  # Pode-se procurar por 'class_=""' se não tiver outra classe
    
    for li in category_items:
        a_tag = li.find('a', class_='category', href=True)  # Encontra o link dentro do <li>
        if a_tag:
            links.append(a_tag['href'])  # Adiciona o href do link à lista
    
    return links

# Teste das funções
if __name__ == '__main__':
    page_content = fetch_page()
    
    if page_content:
        category_links = parse_category_links(page_content)
        print("Links encontrados em 'category-aditional':")
        for link in category_links:
            print(link)
    else:
        print("Falha ao obter o HTML da página.")