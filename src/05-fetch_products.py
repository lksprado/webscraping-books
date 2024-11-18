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

def parse_products(html):
    books = []
    soup = BeautifulSoup(html, 'html.parser')
    
    # Encontra todos os itens de produto
    product_list = soup.find_all('div', class_='product')
    
    for product in product_list:
        # Extraindo as informações de cada produto
        book_name = product.find('a', class_='product-name').get_text(strip=True)  # Corrigido o nome da classe
        book_author = product.find('p', class_='author').get_text(strip=True)  # Corrigido a tag de 'author'
        
        # Verifica se o desconto existe antes de acessar o texto
        book_discount = product.find('div', class_='flag-discount super')
        book_discount = book_discount.get_text(strip=True) if book_discount else "Nenhum desconto"
        
        # Verifica se o preço antigo existe antes de acessar o texto
        book_price_old = product.find('span', class_='price-old')
        book_price_old = book_price_old.get_text(strip=True) if book_price_old else "Preço não disponível"
        
        # Preço novo sempre deve existir, então pode ser acessado diretamente
        book_price_new = product.find('span', class_='price-new').get_text(strip=True)
        
        # Link do produto
        book_url = product.find('a', class_='link-card btn-ripple', href=True)
        
        # Corrigindo o acesso ao atributo href do link
        if book_url:
            book_url = book_url['href']
        
        # Criando o dicionário do livro
        book = {
            'book_name': book_name,
            'book_author': book_author,
            'book_discount': book_discount,
            'book_price_old': book_price_old,
            'book_price_new': book_price_new,
            'book_url': book_url
        }
        
        # Adicionando o livro à lista
        books.append(book)
        
    return books

# Teste das funções
if __name__ == '__main__':
    page_content = fetch_page()
    
    if page_content:
        category_links = parse_products(page_content)
        print("Links encontrados em 'category-aditional':")
        for link in category_links:
            print(link)
    else:
        print("Falha ao obter o HTML da página.")