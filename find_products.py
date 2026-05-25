from bs4 import BeautifulSoup

with open('debug_firstcry.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

print(f"Title: {soup.title.string if soup.title else 'No Title'}")

# Firstcry products are usually in something like <div class="list_block">
blocks = soup.find_all('div', class_=lambda c: c and 'list_block' in c)
print(f"Found {len(blocks)} list_blocks")

# Let's search for "Hot Wheels" text
hw_elements = soup.find_all(string=lambda t: t and 'hot wheels' in t.lower())
print(f"Found {len(hw_elements)} 'hot wheels' texts.")
if hw_elements:
    for el in hw_elements[:5]:
        print(f"Text: {el.strip()}")
        # Get parent a or div
        parent = el.parent
        for _ in range(3):
            if parent:
                print(f"  Parent <{parent.name}> class: {parent.get('class', [])}")
                parent = parent.parent

