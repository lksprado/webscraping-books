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

def parse_ficha_tecnica(ficha_text):
    """
    Função para extrair os campos de EAN, Fabricante e Páginas da ficha técnica
    após a palavra 'Ficha Técnica:'.
    """
    ficha_dict = {}
    
    # Encontrar a parte após "Ficha Técnica:"
    ficha_inicio = ficha_text.find('Ficha Técnica:')
    if ficha_inicio == -1:
        return ficha_dict
    
    ficha_text = ficha_text[ficha_inicio + len('Ficha Técnica:'):].strip()

    # Regex para encontrar padrões de campo: "Campo: Valor"
    pattern = r'([A-Za-zÀ-ÿ\s]+):\s*(.*?)(?=\n[A-Za-zÀ-ÿ\s]+:|$)'
    matches = re.findall(pattern, ficha_text)

    for match in matches:
        campo = match[0].strip()
        valor = match[1].strip()
        
        # Atribuindo o valor ao dicionário
        ficha_dict[campo] = valor
    
    return ficha_dict

def parse_products(html):
    books = []
    soup = BeautifulSoup(html, 'html.parser')

    # Remover tags <script> para não capturar código Javascript
    for script in soup.find_all('script'):
        script.decompose()

    # Encontra a área da descrição do produto
    product_panel = soup.find('div', class_='painel-lateral')
    product_details = soup.find('div', class_='sinopse')
    
    if product_panel and product_details:
        try:
            # Extrai os dados básicos do produto
            book_name = product_panel.find('div', class_='product-name').get_text(strip=True)
            book_author = product_panel.find('div', class_='author').get_text(strip=True)
            book_id = f"{book_name} - {book_author}"

            sinopse = None
            sinopse_div = product_details.find('div')
            if sinopse_div:
                sinopse_paragraphs = sinopse_div.find_all('p')
                sinopse = " ".join([p.get_text(strip=True) for p in sinopse_paragraphs])  # Junta os parágrafos
                #print(f"Sinopse Extraída: {sinopse}")  # Para depuração


            ficha_tecnica = product_details.find('b', string='Ficha Técnica:')

            if ficha_tecnica:
                ficha_tecnica_parent = ficha_tecnica.find_parent('div')

                # A partir da tag <b> Ficha Técnica, procurar as informações subsequentes
                ficha_text = ficha_tecnica_parent.get_text("\n", strip=True)  # Extraímos o texto completo após a ficha técnica
                
                #print(f"Ficha Técnica Extraída: {ficha_text}")  # Para depuração, veja o conteúdo extraído

                # Extraindo os dados da ficha técnica
                ficha_dict = parse_ficha_tecnica(ficha_text)

                # Atribuindo os valores extraídos ao livro
                book = {
                    "book_id": book_id,
                    "book_name": book_name,
                    "book_author": book_author,
                    "sinopse": sinopse,
                    "ean": ficha_dict.get('EAN'),
                    "editora": ficha_dict.get('Fabricante', ficha_dict.get('Editora')),
                    "paginas": ficha_dict.get('Páginas', ficha_dict.get('Número de Páginas')),
                    "idioma": ficha_dict.get('Idioma'),
                    "isbn": ficha_dict.get('ISBN'),
                    "idade_minima": ficha_dict.get('Idade mínima')
                }
                books.append(book)
            else:
                print("Ficha Técnica não encontrada.")
        except AttributeError as e:
            print(f"Erro ao processar a ficha técnica: {e}")

    return books



# Exemplo de uso
url = 'https://livraria.sensoincomum.org/nossos-mortos'
html = fetch_page(url)
if html:
    books = parse_products(html)
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