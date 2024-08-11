import requests
from bs4 import BeautifulSoup
import os

URL = 'https://www.ontario.ca/document/official-mto-drivers-handbook/signs'


def image_downloader(url, folder):
    new_folder = os.path.join(os.getcwd(), folder)
    try:
        os.mkdir(new_folder)
    except:
        pass

    os.chdir(new_folder)

    r = requests.get(url)

    soup = BeautifulSoup(r.text, 'html.parser')

    images = soup.find_all('img')

    names = {}
    for image in images:
        link = image['src']
        name = image['alt']
        if name in names:
            names[name] = names[name] + 1
            name = name + str(names[name])
        else:
            names[name] = 1
        with open(name + '.jpg', 'wb') as f:
            if link.startswith('//'):
                link = 'https:' + link
                print(link)
            elif link.startswith('/'):
                link = 'https://www.ontario.ca' + link
                print(link)
            im = requests.get(link)
            f.write(im.content)
            print('Writing: ', name)


image_downloader(URL, 'signs')