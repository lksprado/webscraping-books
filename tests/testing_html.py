from bs4 import BeautifulSoup

html = """
<div id="column-right">
 <div class="alone">
  <div class="back-sub-category">
   <i class="fas fa-chevron-left"></i>
  </div>
  <div class="parent-categ">
   Filosofia
  </div>
 </div>
</div>
"""

soup = BeautifulSoup(html, 'html.parser')
category = soup.find('div', class_='parent-categ')
if category:
    print(category.get_text(strip=True))
else:
    print("Categoria não encontrada!")