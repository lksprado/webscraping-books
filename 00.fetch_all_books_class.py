import requests
from bs4 import BeautifulSoup
import re 
import csv
import pytz
from datetime import datetime

class BookScraper:
    """Scraps livraria do senso incomum"""
    def __init__(self, base_url):
        self.url = base_url
        self.headers =  {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }
        self.max_retries = 3
        self.retry_delay = 3

        
    # MÉTODO DEVOLVE HTML DA URL 
    def fetch_page(self, url_new:str = ''):
        """Retorna html da URL"""
        url = self.url + url_new
        try:
            for attempt in range(self.max_retries):
                print(f"Connecting to URL: {url} - Attempt: {attempt + 1}")
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                return response.text
        
        except requests.exceptions.RequestException as e:
            print(f"Error acessing page: {e}")
            return None
    
    # MÉTODO OBTEM TODOS OS LINKS PRINCIPAIS
    def get_all_links(self, remove: set):
        """Obtém todos links internos"""
        html = self.fetch_page()
        if not html:
            return set()
        soup = BeautifulSoup(html, 'html.parser')
        pages = set()
        pages_to_remove = remove
        
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


    def parse_products(self,html):
        """Retorna livros das pagina"""
        books = []
        if not html:
            return books
        book_category_or_subcategory = None
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            # Encontra todos os itens de produto
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
            
            product_list = soup.find_all('div', class_='product')
            for product in product_list:
                book_name = product.find('a', class_='product-name')
                book_author = product.find('p', class_='author')
                book_discount = product.find('div', class_='flag-discount super')
                book_price_old = product.find('span', class_='price-old')
                book_price_new = product.find('span', class_='price-new')
                book_url = product.find('a', class_='link-card btn-ripple', href=True)

                books.append({
                    'book_id': f"{book_name.get_text(strip=True)} - {book_author.get_text(strip=True)}" if book_name and book_author else None,
                    'book_name': book_name.get_text(strip=True) if book_name else None,
                    'book_author': book_author.get_text(strip=True) if book_author else None,
                    'book_category': book_category_or_subcategory,
                    'book_discount': book_discount.get_text(strip=True) if book_discount else None,
                    'book_price_old': book_price_old.get_text(strip=True) if book_price_old else None,
                    'book_price_new': book_price_new.get_text(strip=True) if book_price_new else None,
                    'book_url': f"{self.url}/{book_url['href']}" if book_url else None,
                    'time': datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%Y-%m-%d %H:%M:%S')
                })
        except Exception as e:
            print(f"Error parsing products: {e}")
        return books


    # MÉTODO ACESSA TODAS PÁGINAS DOS LINKS
    def access_page(self, page_set: set):
        """Obtém numero das paginas das categoriais e subcategorias"""
        all_books = []
        regex = r"(?<=\?page=)\d+"

        for page in page_set:
            html = self.fetch_page(page)
            if not html:
                continue
            all_books.extend(self.parse_products(html))

            soup = BeautifulSoup(html, 'html.parser')
            page_numbers = set()
            page_items = soup.find_all('div', class_='links')
            for link_div in page_items:
                for page_link in link_div.find_all('a', href=True):
                    match = re.search(regex, page_link['href'])
                    if match:
                        page_numbers.add(int(match.group()))

            for following_page in range(2, max(page_numbers, default=2) + 1):
                html = self.fetch_page(f"{page}?page={following_page}")
                all_books.extend(self.parse_products(html))

        return all_books

# MÉTODO PARA SALVAR EM CSV
def save_to_csv(books, filename):
    if books:
        keys = books[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=keys, delimiter=';', quotechar='"')
            writer.writeheader()
            writer.writerows(books)

if __name__ == '__main__':
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
        '/index.php?route=product/category&path=93',
        '/index.php?route=product/category&path=117',
        '/index.php?route=product/category&path=110',
        '/index.php?route=product/category&path=98',
        '/index.php?route=product/category&path=102',
    }
    senso = BookScraper('https://livraria.sensoincomum.org/')
    pages = senso.get_all_links(pages_to_remove)
    books = senso.access_page(pages)
    if books:
        save_to_csv(books, '00-livros_raw.csv')
    