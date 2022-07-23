import json
import os.path
import requests
from bs4 import BeautifulSoup

headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36'}

class Specification:
    def __init__(self, name, link):
        self.name = name
        self.link = link
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return '{} ({})'.format(self.name, self.link)
    class Encoder(json.JSONEncoder):
        def default(self, o):
            return o.__dict__

def getSpecifications(soup):
    return [Specification(article.a.get_text(), article.a['href']) for article in soup.find_all('article')]

def getPageCount(soup):
    return int(soup.find_all('li', 'page-item')[-2].a.get_text())

def getPages(n):
    specifications = []
    for i in range(2, n + 1):
        path = 'https://www.bluetooth.com/spec-types/gatt/page/{}/'.format(i)
        r = requests.get(path, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        specifications.extend(getSpecifications(soup))
    return specifications

def writePDF(name, content):
    #with open('./pdf/{}.pdf'.format(name), 'wb') as f:
    with open(os.path.join('./pdf/', name.replace('/', ' ') + '.pdf'), 'wb') as f:
        f.write(content)

def getPDF(specification):
    print(specification['link'])
    r = requests.get(specification['link'], headers=headers)
    print(r.status_code)
    if r.headers['Content-Type'] == 'application/pdf' or r.headers['Content-Type'] == 'application/x-pdf':
        writePDF(specification['name'], r.content)
        return
    soup = BeautifulSoup(r.text, 'html.parser')
    meta = soup.find('ul', 'card-meta')
    if meta is None:
        print('ERROR: No metadata')
        return
    path = meta.div.a['href']
    r = requests.get(path, headers=headers)
    writePDF(specification['name'], r.content)

# TODO: Check for the existence of index.html
r = requests.get('https://www.bluetooth.com/spec-types/gatt/', headers=headers)
print(r.status_code)
soup = BeautifulSoup(r.text, 'html.parser')

with open('index.html', 'w') as f:
    f.write(r.text)

# TODO: Check for the existence of gatt-specifications.json
with open('index.html', 'r') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

specifications = getSpecifications(soup)
page_count = getPageCount(soup)
specifications.extend(getPages(page_count))

with open('gatt-specifications.json', 'w') as f:
    f.write(json.dumps(specifications, cls=Specification.Encoder))

with open('gatt-specifications.json', 'r') as f:
    specifications = json.load(f)

for spec in specifications:
    # TODO: Check for the existence of each PDF
    getPDF(spec)
