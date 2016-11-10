import requests
import lxml.html


def get_abs_link(rel_link):
    return 'https://www.vorleser.net/{}'.format(rel_link)

author_url = 'https://www.vorleser.net/autor.html'
print('fetching: ' + author_url)
author_site_html = requests.get(author_url)
dom = lxml.html.fromstring(author_site_html.content)

author_links = []
# select the url in href for all a tags(links)
for link in dom.xpath('//a/@href'):
    if '/autor.html' in link:
        link = get_abs_link(link)
        if link not in author_links:
            author_links.append(link)
            print(link)
            with open('q_author_sites', 'a') as f:
                f.write(link + '\n')

book_site_links = []
for link in author_links:
    link = get_abs_link(link)
    print('fetching: ' + link)
    author_html = requests.get(link)
    dom = lxml.html.fromstring(author_html.content)
    for book_site_link in dom.xpath('//a/@href'):
        if '/hoerbuch.html' in book_site_link:
            book_site_link = get_abs_link(book_site_link)
            if book_site_link not in book_site_links:
                book_site_links.append(book_site_link)
                if book_site_link not in book_site_links:
                    print(book_site_link)
                    with open('q_book_sites', 'a') as f:
                        f.write(book_site_link + '\n')

book_links = []
for link in book_site_links:
    link = get_abs_link(link)
    print('fetching: ' + link)
    book_html = requests.get(link)
    dom = lxml.html.fromstring(book_html.content)
    for book_link in dom.xpath('//a/@href'):
        if 'https://www.vorleser.net/f-Download-d-audiobook.html?id' in book_link:
            if book_link not in book_links:
                print(book_link)
                with open('q_books', 'a') as f:
                    f.write(book_link + '\n')
