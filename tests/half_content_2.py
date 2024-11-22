import requests
from bs4 import BeautifulSoup

def fetch_page():
    url = 'https://livraria.sensoincomum.org/recebe-maria-como-tua-esposa'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Garante que a resposta foi bem-sucedida
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

    return books

# def parse_page(html):
#     # Parsear o HTML
#     soup = BeautifulSoup(html, 'html.parser')
    
#     product_panel = soup.find('div', class_='painel-lateral')
#     product_details = soup.find('div', class_='sinopse')
#     if product_panel and product_details:
#         # Extrai os dados básicos do produto
#         book_name = product_panel.find('div', class_='product-name').get_text(strip=True)
#         book_author = product_panel.find('div', class_='author').get_text(strip=True)
#         book_id = f"{book_name} - {book_author}"

#         sinopse = None
#         sinopse_div = product_details.find('div')
#         if sinopse_div:
#             sinopse_paragraphs = sinopse_div.find_all('p')
#             sinopse = " ".join([p.get_text(strip=True) for p in sinopse_paragraphs])  # Junta os parágrafos
#             #print(f"Sinopse Extraída: {sinopse}")  # Para depuração

#     # Procurar "Ficha Técnica" de forma flexível
#     ficha_tecnica = soup.find_all(string=lambda text: "Ficha Técnica" in text)
        
#     if not ficha_tecnica:
#         return "Ficha Técnica não encontrada."
    
#     resultados = {}
    
    for item in ficha_tecnica:
        # Debug: Verificar o elemento pai
        #print("Elemento com 'Ficha Técnica':", item)
        
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
                resultados[chave.strip()] = valor.strip()
    
    return resultados


def save_to_file(content: str, filename: str):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Conteúdo salvo em {filename}")

if __name__ == '__main__':
    page_content = fetch_page()
    
    if page_content:
        parsed_content = parse_page(page_content)
        print(parsed_content)  # Exibe o HTML formatado
        
        # Salva o conteúdo formatado em um arquivo de texto
        #save_to_file(parsed_content, 'descricao_comum_limited3.txt')
    else:
        print("Falha ao obter o HTML da página.")