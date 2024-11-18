import requests

url = "https://livraria.sensoincomum.org/robots.txt"
response = requests.get(url)
print(response.text)
