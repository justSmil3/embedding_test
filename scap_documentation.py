from urllib.request import urlopen
from bs4 import BeautifulSoup

def get_links(soup):
    link_list = soup.find_all('a')
    links = []
    
    for item in link_list:
        if(item.get('class') == ['see-more']):
            continue
        tmp = item.get('href')
        if '/support/solutions/folders/' in tmp and '-' not in tmp:
            links.append("https://bitethebytes.freshdesk.com" + item.get('href'))
    return links;

def get_child_links(html_soup):
    links = []
    link_list = html_soup.find_all('a')

    for link in link_list:
        if link.get('class') == ['c-link']:
            links.append("https://bitethebytes.freshdesk.com" + link.get('href'))
    return links

def get_children_links(soup_list):
    links = []
    for soup in soup_list:
        links.append(get_child_links(soup))
    return links
        

def get_soups(link_list, first = False):
    soups = []
    pages = []
    for link in link_list:
        link_page = urlopen(link)
        soup = BeautifulSoup(link_page, 'html.parser')
        soups.append(soup)
        if first:
            subpages = soup.find('div', {'class': 'pagination'})
            if subpages is None:
                continue
            subpages = subpages.findChildren("ul")[0].findChildren("li")[2:-1]
            i = 2
            for _ in subpages:
                new_link_page = urlopen(link+"/page/{}".format(i))
                i+=1
                soup = BeautifulSoup(new_link_page, 'html.parser')
                soups.append(soup)
    return soups

def extract_text(soup):
    text = soup.get_text("|", strip=True)
    text_list = text.split('|')
    text_list = text_list[13:len(text_list)-6]
    del text_list[1:3]
    text_list[0] += ':'
    for tmp in text_list:
        if tmp.startswith("Next:"):
            text_list.remove(tmp)
    result_text = ' '.join(text_list)
    return result_text

def extract_all_texts(soups):
    texts = []
    for soup in soups:
        text = extract_text(soup)
        if not text.startswith ("Video"):
            texts.append(text)
    return texts

def extract_documentation():
    results = []
    url = "https://bitethebytes.freshdesk.com/support/solutions"
    index_page = urlopen(url)
    index_soup = BeautifulSoup(index_page, 'html.parser')
    links_depth_0 = get_links(index_soup)
    soups_depth_0 = get_soups(links_depth_0, True)
    links_depth_1 = get_children_links(soups_depth_0)
    soups_depth_1 = []
    for links in links_depth_1:
        soups = get_soups(links)
        soups_depth_1.append(soups)
    for soups in soups_depth_1:
        print(len(extract_all_texts(soups)))
        results.extend(extract_all_texts(soups))
    print(len(results))
    return results

if __name__ == "__main__":
    texts = extract_documentation();
    #for text in texts: 
    #    print(text)
    #    print("\n")

