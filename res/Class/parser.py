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

    def get_items(self, limit=3, except_ads=True):
        #에러 처리
        if not self.url.startswith("https://www.coupang.com/np/search?component=&q=") or not isinstance(limit, int):
            raise TypeError
        if limit <= 0:
            raise IndexError
        
        items_group = self.bs.find("ul", {"id": "productList"}).find_all("li")
        
        # 파싱해온 그룹에서 count 갯수만큼 뽑음, 광고 제거는 선택
        items_list = []
        item_count = 0
        for item in items_group:
            if ('search-product__ad-badge' not in item.get("class")) or except_ads:
                items_list.append(item)
                item_count += 1
            if item_count >= limit:
                break
            
        # 정보 뽑아 output 사전에 저장한다.
        return [{
            "name": item.find("dd", {"class": "descriptions"}).find("div", {"class": "name"}).text,
            "url": "https://www.coupang.com%s" % item.find("a").get("href"),
            "image_url": "https:%s" % item.find("dt", {"class": "image"}).find("img").get("src"),
            "product_id": item.get("data-product-id"),
            "is_ad": 'search-product__ad-badge' in item.get("class"),
            "is_rocket": (item.get("data-is-rocket") != ""),
            "price": item.find("strong", {"class": "price-value"}).text,
            "base_price": item.find("del", {"class": "base-price"}).text if item.find("del", {"class": "base-price"}) != None else "",
            "discount_rate": item.find("span", {"class": "instant-discount-rate"}).text if item.find("span", {"class": "instant-discount-rate"}) != None else "",
            "rating": item.find("em", {"class": "rating"}).text,
            "rating_count": item.find("span", {"class": "rating-total-count"}).text
        } for item in items_list]
        

if __name__ == "__main__":
    parser = parser("https://www.coupang.com/np/search?component=&q=%EA%B2%80%EC%83%89&channel=user")
    print(parser.get_items(1))
