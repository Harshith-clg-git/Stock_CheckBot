from bs4 import BeautifulSoup

with open('bb_product.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

print(f"Title: {soup.title.string if soup.title else 'No Title'}")

hw_elements = soup.find_all(string=lambda t: t and 'hot wheels' in t.lower())
print(f"Found {len(hw_elements)} hot wheels texts.")
for el in hw_elements[:5]:
    parent = el.parent
    if parent:
        print(f"Text: {el.strip()}, Tag: {parent.name}, Class: {parent.get('class', [])}")
        p2 = parent.parent
        if p2: print(f"  Parent: {p2.name} Class: {p2.get('class', [])}")
