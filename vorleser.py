import requests
import lxml.html
from os import path, makedirs
from json import dump


class VorleserScraper(object):
    ''' writes a books.json in the form:
        {'<author_name>': [{booktitle: 'title of book one', url: 'downloadurl 1'}, {...}]...}
        and downloads all mp3 in this hierarchy:
        <author_name>
          |- booktitle1.mp3
          |- ...
    '''
    base_url = 'https://www.vorleser.net/'

    def __init__(self):
        self.books = {}
        self.book_links = []
        self.cookies = requests.get(self.base_url).cookies

    def mkdir(self, destination):
        if not path.exists(destination):
            makedirs(destination)

    def download(self, url, destination, filename):
        self.mkdir(destination)
        filepath = destination + '/' + filename + '.mp3'
        print('checking {}'.format(filepath))
        if path.exists(filepath):
            print('file {} already exists. Skipping'.format(filepath))
            return

        print('downloading {} as {}'.format(url, filepath))
        with open(filepath, 'wb') as handle:
            response = requests.get(url, cookies=self.cookies, stream=True)
            if not response.ok:
                pass

            for block in response.iter_content(1024):
                handle.write(block)

    def get_abs_link(self, rel_link):
        return 'https://www.vorleser.net/{}'.format(rel_link)

    def get_links_containing(self, url, substring):
        html = requests.get(url)
        dom = lxml.html.fromstring(html.content)

        links = []
        for link in dom.xpath('//a/@href'):
            if substring in link:
                link = self.get_abs_link(link)
                if link not in links:
                    links.append(link)

        return links

    def add_book(self, url):
        html = requests.get(url)
        dom = lxml.html.fromstring(html.content)
        title = dom.xpath('//*[@id="site-wrapper"]/div[1]/div/div/div[2]/div[1]/div[2]/h2/text()')[0]
        # escape /
        title = title.replace("/", " ")
        author = dom.xpath('//*[@id="site-wrapper"]/div[1]/div/div/div[2]/div[1]/div[2]/h5/a/text()')[0]
        for link in dom.xpath('//a/@href'):
            link = self.get_abs_link(link)
            if 'https://www.vorleser.net/f-Download-d-audiobook.html?id' in link:
                url = link

        if author in self.books:
            # only insert new books
            if url not in self.book_links:
                self.books[author].append({'title': title, 'author': author, 'url': url})
                self.book_links.append(url)
        else:
            self.books[author] = [{'title': title, 'author': author, 'url': url}]

    def get_book_links(self):
        author_url = 'https://www.vorleser.net/autor.html'
        author_page_links = self.get_links_containing(author_url, '/autor.html')
        book_page_links = []
        for author_page_link in author_page_links:
            book_page_links = book_page_links + self.get_links_containing(author_page_link, '/hoerbuch.html')
            print('scraping: {}'.format(author_page_link))

        for book_page_link in book_page_links:
            print('scraping: {}'.format(book_page_link))
            self.add_book(book_page_link)

        with open('books.json', 'w') as handle:
            dump(self.books, handle)
        print(self.books)

    def download_books(self):
        for k, v in self.books.items():
            for book in v:
                self.download(book['url'], k, book['title'])

if __name__ == "__main__":
    vorleser = VorleserScraper()
    vorleser.get_book_links()
    vorleser.download_books()
