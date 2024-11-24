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

def get_all_links(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    pages = set()

    # Lista de categorias principais a serem removidas
    pages_to_remove = {
        'camisetas',
        'medicina-profissional-e-tecnico',
        '/index.php?route=product/category&path=136',
        'index.php?route=product/manufacturer',
        'cat-turismo',
        'ofertas-senso',
        '/index.php?route=product/category&path=150',
        'documentario',
        '/index.php?route=product/category&path=63',
        '/index.php?route=product/author',
        '/index.php?route=product/category&path=145',
        'oferta-relampago-senso-incomum',
        '/vendas-internacionais?local=de',
        '/vendas-internacionais?local=uk',
        '/vendas-internacionais?local=fr',
        '/vendas-internacionais?local=us',
        '/vendas-internacionais?local=pt',
        '/vendas-internacionais?local=jp',
        '/vendas-internacionais?local=es',
        '/vendas-internacionais?local=it',
    }
    
    # Encontra todas as categorias principais (li com class "with-child")
    category_items = soup.find_all('li', class_='with-child') 
    
    for li in category_items:
        # Categoria principal (a tag diretamente dentro do li)
        main_category = li.find('a', class_='category', href=True)
        if main_category:
            main_href = main_category['href']
            
            # Ignora essa categoria e suas subcategorias se a principal estiver em pages_to_remove
            if main_href in pages_to_remove:
                continue

            # Adiciona a categoria principal
            pages.add(main_href)
        
        # Subcategorias (ul com class "sub-cat")
        sub_categories = li.find('ul', class_='sub-cat')
        if sub_categories:
            sub_category_links = sub_categories.find_all('a', href=True)
            for sub_category in sub_category_links:
                sub_href = sub_category['href']
                # Apenas adiciona subcategorias se a categoria principal não for excluída
                pages.add(sub_href)
    pages -= pages_to_remove
    return pages

if __name__ == '__main__':
    page_content = fetch_page()
    
    if page_content:
        category_links = get_all_links(page_content)
        print("Links encontrados nos destaques:\n")
        for link in category_links:
            print(link)
    else:
        print("Falha ao obter o HTML da página.")
