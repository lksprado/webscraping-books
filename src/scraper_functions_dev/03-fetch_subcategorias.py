# OBTEM OS LINKS CATEGORIAS



import requests
from bs4 import BeautifulSoup

def fetch_page():
    url = 'https://livraria.sensoincomum.org/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a página: {e}")
        return None


def parse_with_child_category_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    pages = set()
    
    # Encontra todos os elementos <li> com a classe 'with-child'
    category_items = soup.find_all('li', class_='with-child')
    
    for li in category_items:
        # Encontra as subcategorias dentro da tag <ul class='sub-cat'>
        sub_categories = li.find('ul', class_='sub-cat')
        if sub_categories:
            sub_category_links = sub_categories.find_all('a', href=True)
            for sub_category in sub_category_links:
                pages.add(sub_category['href'])  # Adiciona o link das subcategorias

    return pages

# Teste das funções
if __name__ == '__main__':
    page_content = fetch_page()
    
    if page_content:
        category_links = parse_with_child_category_links(page_content)
        print("Links encontrados:\n")
        for link in category_links:
            print(link)
    else:
        print("Falha ao obter o HTML da página.")
        
        

# def parse_with_child_category_links(html):
#     soup = BeautifulSoup(html, 'html.parser')
#     links = []
    
#     # Encontra todos os elementos <li> com a classe 'with-child'
#     category_items = soup.find_all('li', class_='with-child')
    
#     for li in category_items:
#         # Encontra o link principal da categoria
#         main_category_a_tag = li.find('a', class_='category', href=True)
#         if main_category_a_tag:
#             main_category_link = main_category_a_tag['href']
#             links.append(main_category_link)  # Adiciona o link principal
            
#             # Encontra as subcategorias dentro da tag <ul class='sub-cat'>
#             sub_categories = li.find('ul', class_='sub-cat')
#             if sub_categories:
#                 sub_category_links = sub_categories.find_all('a', href=True)
#                 for sub_category in sub_category_links:
#                     links.append(sub_category['href'])  # Adiciona o link das subcategorias
    
#     return links