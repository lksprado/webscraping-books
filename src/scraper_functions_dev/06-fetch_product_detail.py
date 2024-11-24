import requests
from bs4 import BeautifulSoup
import re

def fetch_page(url):
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

def parse_page(html):
    # Inicializar variáveis
    books = []

    # Parsear o HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Procurar os detalhes do produto
    product_panels = soup.find_all('div', class_='painel-lateral')
    product_details_list = soup.find_all('div', class_='sinopse')
    
    for product_panel, product_details in zip(product_panels, product_details_list):
        book_id = None
        sinopse = None

        try:
            if product_panel and product_details:
                # Extrai os dados básicos do produto
                book_name = product_panel.find('div', class_='product-name').get_text(strip=True)
                book_author = product_panel.find('div', class_='author').get_text(strip=True)
                book_id = f"{book_name} - {book_author}"

                # Extrair a sinopse antes da "Ficha Técnica"
                sinopse_div = product_details.find('div')
                if sinopse_div:
                    sinopse_paragraphs = sinopse_div.find_all('p')
                    sinopse = " ".join([p.get_text(strip=True) for p in sinopse_paragraphs])  # Junta os parágrafos

                # Procurar "Ficha Técnica" de forma flexível
                ficha_tecnica = soup.find_all(string=lambda text: "Ficha Técnica" in text)

                if ficha_tecnica:
                    ficha_dict = {}
                    for item in ficha_tecnica:
                        # Procurar todos os elementos subsequentes após "Ficha Técnica"
                        next_elements = item.find_all_next(string=True)
                        for element in next_elements:
                            text = element.strip()
                            # Ignorar strings vazias
                            if not text:
                                continue
                            # Verificar se alcançamos o fim dos dados relevantes
                            if "//<![CDATA" in text:
                                break
                            # Procurar chave e valor
                            if ":" in text:
                                chave, valor = text.split(":", 1)
                                ficha_dict[chave.strip()] = valor.strip()

                    book = {
                        'book_id': book_id,
                        'sinopse': sinopse,
                        'ean': ficha_dict.get('EAN'),
                        'editora': ficha_dict.get('Fabricante', ficha_dict.get('Editora')),
                        'paginas': ficha_dict.get('Páginas', ficha_dict.get('Número de Páginas')),
                        'idioma': ficha_dict.get('Idioma'),
                        'isbn': ficha_dict.get('ISBN'),
                        'idade_minima': ficha_dict.get('Idade mínima')
                    }
                    books.append(book)
                else:
                    print(f"Ficha Técnica não encontrada para o livro: {book_name}")
        except AttributeError as e:
            print(f"Erro ao processar o produto: {e}")

    return books


# Exemplo de uso
#url = 'https://livraria.sensoincomum.org/nossos-mortos'
#url = 'https://livraria.sensoincomum.org/inteligencia-e-logos'
url = 'https://livraria.sensoincomum.org/recebe-maria-como-tua-esposa'
html = fetch_page(url)
if html:
    books = parse_page(html)
    for book in books:
        print(book)


# def parse_products(html):
#     books = []
#     soup = BeautifulSoup(html, 'html.parser')
    
#     # Encontra todos os itens de produto
#     product_panel = soup.find('div', class_='painel-lateral')
#     product_detail = soup.find_all('div', class_='item detail')
    
#     if product_panel:
#         try:
#             # Extrai os dados básicos do produto
#             book_name = product_panel.find('div', class_='product-name').get_text(strip=True)
#             book_author = product_panel.find('div', class_='author').get_text(strip=True)
#             book_id = f"{book_name} - {book_author}"

#             # Localiza os detalhes do produto
#             product_details = soup.find('div', class_='description')
#             if product_details:
#                 paginas = product_details.find('label', string='Páginas')
#                 if paginas:
#                     paginas = paginas.find_next('span').get_text(strip=True)
#                 else:
#                     print("Páginas não encontrado")
                
#                 idioma = product_details.find('label', string='Idioma')
#                 if idioma:
#                     idioma = idioma.find_next('span').get_text(strip=True)
#                 else:
#                     print("Idioma não encontrado")
                
#                 isbn = product_details.find('label', string='ISBN')
#                 if isbn:
#                     isbn = isbn.find_next('span').get_text(strip=True)
#                 else:
#                     print("ISBN não encontrado")

#                 ean = product_details.find('label', string='EAN')
#                 if ean:
#                     ean = ean.find_next('span').get_text(strip=True)
#                 else:
#                     print("ISBN não encontrado")
                
#                 editora = None
#                 possible_selectors = [
#                     '#content > div > div.product-info.with-related > div > div.description > div:nth-child(1) > span > a',
#                     '#content > div > div.product-info.with-related > div > div.description > div:nth-child(2) > span > a',
#                     '#content > div > div.product-info.with-related > div > div.description > div:nth-child(3) > span > a',
#                     '#content > div > div.product-info.with-related > div > div.description > div:nth-child(4) > span > a',
#                     '#content > div > div.product-info.with-related > div > div.description > div:nth-child(5) > span > a',
#                     '#content > div > div.product-info.with-related > div > div.description > div:nth-child(4) > span > a',
#                     '#content > div > div.product-info.with-related > div > div.description > div:nth-child(6) > span > a'
#                 ]
#                 for selector in possible_selectors:
#                     editora_element = soup.select_one(selector)
#                     if editora_element:
#                         editora = editora_element.get_text(strip=True)
#                         break
#                 if not editora:
#                     print("Editora não encontrada")
                    
#                 idade_minima = product_details.find('label', string='Idade mínima')
#                 if idade_minima:
#                     idade_minima = idade_minima.find_next('span').get_text(strip=True)
#                 else:
#                     print("Idade minima não encontrado")
#             # Adiciona os dados à lista de tuplas
#             book = (
#                 book_id,
#                 book_name,
#                 book_author,
#                 paginas,
#                 idioma,
#                 isbn,
#                 ean,
#                 editora,
#                 idade_minima
#             )
#             books.append(book)
#         except AttributeError as e:
#             print(f"Erro ao processar o produto: {e}")
    
#     return books