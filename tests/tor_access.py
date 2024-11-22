import socks
import socket
import requests

socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, 'localhost', 9050)
socket.socket = socks.socksocket
response = requests.get('http://icanhazip.com')
print(response.text)
