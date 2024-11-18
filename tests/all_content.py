import requests
from bs4 import BeautifulSoup

def fetch_page():
    url = 'https://livraria.sensoincomum.org/filosofia'
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
    soup = BeautifulSoup(html, 'html.parser')
    # Usamos o método prettify para formatar o HTML
    return soup.prettify()

# Teste das funções
if __name__ == '__main__':
    page_content = fetch_page()
    
    if page_content:
        parsed_content = parse_page(page_content)
        print("HTML formatado da página:")
        print(parsed_content)  # Exibe o HTML formatado
    else:
        print("Falha ao obter o HTML da página.")