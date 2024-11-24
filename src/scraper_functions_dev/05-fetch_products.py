# OBTEM OS LINKS CATEGORIAS
import requests
from bs4 import BeautifulSoup

def fetch_page():
    url = 'https://livraria.sensoincomum.org/camisetas'
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


def parse_products(html):
    books = []
    book_category_or_subcategory = None
    soup = BeautifulSoup(html, 'html.parser')
    
    try:
        # Encontra todos os itens de produto
        product_list = soup.find_all('div', class_='product')
        column_right = soup.find('div', id='column-right')
        
        if column_right:
            # Tenta primeiro encontrar a subcategoria
            book_subcategory_element = column_right.find('div', class_='sub-alone')
            if book_subcategory_element:
                book_category_or_subcategory = book_subcategory_element.get_text(strip=True)
            else:
                # Se não encontrou a subcategoria, tenta encontrar a categoria
                book_category_element = column_right.find('div', class_='parent-categ')
                if book_category_element:
                    book_category_or_subcategory = book_category_element.get_text(strip=True)
        
        
        
        for product in product_list:
            book_name = product.find('a', class_='product-name').get_text(strip=True) if book_name else None
            book_author = product.find('p', class_='author').get_text(strip=True) if book_author else None
            book_id = f"{book_name} - {book_author}"
            book_discount = product.find('div', class_='flag-discount super')
            book_discount = book_discount.get_text(strip=True) if book_discount else None
            book_price_old = product.find('span', class_='price-old')
            book_price_old = book_price_old.get_text(strip=True) if book_price_old else None
            book_price_new = product.find('span', class_='price-new').get_text(strip=True) if book_price_new else None
            book_url = product.find('a', class_='link-card btn-ripple', href=True) if book_url else None
            if book_url:
                book_url = book_url['href']
            book = {
                'book_id': book_id,
                'book_name': book_name,
                'book_author': book_author,
                'book_category': book_category_or_subcategory,
                'book_discount': book_discount,
                'book_price_old': book_price_old,
                'book_price_new': book_price_new,
                'book_url': f"https://livraria.sensoincomum.org/{book_url}"
            }
            books.append(book)
        
    except Exception:
        books = []
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