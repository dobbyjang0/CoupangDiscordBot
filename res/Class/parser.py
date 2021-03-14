import bs4
import requests

class parser:
    def __init__(self, url):
        self.url = url
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
        self.hdr = self.header

    @property
    def bs(self):
        session = requests.Session()
        html = session.get(self.url, headers=self.hdr).content
        return bs4.BeautifulSoup(html, 'lxml')

    @property
    def items(self):
        wrapper = self.bs.find("div", {"class": "search-wrapper"})
        result_count = wrapper.find("div", {"class": "search-query-result"}).find_all("strong")[1].text
        items = wrapper.find("ul", {"class": "search-product-list"}).find_all("li")
        return [{
            "name": item.find("dd", {"class": "descriptions"}).find("div", {"class": "name"}).text,
            "image_url": "https:%s" % item.find("dt", {"class": "image"}).find("img").get("src")
        } for item in items]
