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
    def status_code(self):
        return requests.get(self.url).status_code

    def get_items(self, limit=3, is_except_ads=True):
        if not self.url.startswith("https://www.coupang.com/np/search?component=&q="):
            raise TypeError

        assert isinstance(limit, int), "정수가 아닙니다."
        if limit <= 0:
            raise IndexError

        items_page = self.bs.find("ul", {"id": "productList"})
        if not items_page:
            raise
        else:
            items_group = items_page.find_all("li")


        items = []
        while limit:
            if item.get("class") != 'search-product__ad-badge' or is_except_ads:
                items.append(item)
                limit -= 1

        datas = []
        for item in items:
            data = {
                "name": item.find("dd", {"class": "descriptions"}).find("div", {"class": "name"}).text,
                "url": "https://www.coupang.com%s" % item.find("a").get("href"),
                "image_url": "https:%s" % item.find("dt", {"class": "image"}).find("img").get("src"),
                "product_id": item.get("data-product-id"),
                "is_ad": item.get("class") == "search-product__ad-badge",
                "is_rocket": item.get("data-is-rocket") != "",
                "price": item.find("strong", {"class": "price-value"}).text,
                "base_price": None,
                "discount_rate": None,
                "rating": item.find("em", {"class": "rating"}).text,
                "rating_count": item.find("span", {"class": "rating-total-count"}).text
            }

            if (base_price := item.find("del", {"class": "base-price"})):
                data.update({
                    "base_price": base_price.text
                })

            if (discount_rate := item.find("span", {"class": "instant-discount-rate"})):
                data.update({
                    "discount_rate": discount_rate.text
                })
            datas.append(data)
        return datas

if __name__ == "__main__":
    parser = parser("https://www.coupang.com/np/search?component=&q=%EA%B2%80%EC%83%89&channel=user")
    print(parser.get_items(1))
