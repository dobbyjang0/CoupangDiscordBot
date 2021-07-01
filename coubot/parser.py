import bs4
import requests

from coubot import check


def text_safety(bs):

    if not bs:
        return ""

    return bs.text


class Parser:
    def __init__(self, url):
        self.url = url
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }

    @property
    def hdr(self):
        return self.header

    @property
    def bs(self):
        session = requests.Session()
        html = session.get(self.url, headers=self.hdr).content
        return bs4.BeautifulSoup(html, 'lxml')

    @property
    def status_code(self):
        return requests.get(self.url).status_code

    def get_items(self, limit=3, is_except_ads: bool = True):
        # 에러 처리
        check.check().is_startswith(self.url, "https://www.coupang.com/np/search?component=&q=")

        assert isinstance(limit, int), "limit은 정수여야합니다."
        assert limit >= 0, "limit은 0보다 커야합니다."
        
        items_page = self.bs.find("ul", {"id": "productList"})

        if items_page is None:
            return None

        items_group = self.bs.find("ul", {"id": "productList"}).find_all("li")
        _items_group = iter(items_group)

        # 파싱해온 그룹에서 count 갯수만큼 뽑음, 광고 제거는 선택
        items_list = []

        while limit:
            now_item = next(_items_group)
            if "search-product__ad-badge" not in now_item.get("class") or is_except_ads:
                items_list.append(now_item)
                limit -= 1

        # 정보 뽑아 output 사전에 저장한다.
        datas = []
            
        for item in items_list:
            data = {
                "name": item.find("dd", {"class": "descriptions"}).find("div", {"class": "name"}).text,
                "url": "https://www.coupang.com%s" % item.find("a").get("href"),
                "image_url": "https:%s" % item.find("dt", {"class": "image"}).find("img").get("src"),
                "product_id": item.get("data-product-id"),
                "is_ad": item.get("class") == "search-product__ad-badge",
                "is_rocket": item.get("data-is-rocket") != "",
                "price": text_safety(item.find("strong", {"class": "price-value"})),
                "base_price": text_safety(item.find("del", {"class": "base-price"})),
                "discount_rate": text_safety(item.find("span", {"class": "instant-discount-rate"})),
                "rating": text_safety(item.find("em", {"class": "rating"})),
                "rating_count": text_safety(item.find("span", {"class": "rating-total-count"}))
            }
                
            datas.append(data)
            
        return datas
    
    def get_item_detail(self):
        #에러 처리
        
        if not self.url.startswith("https://www.coupang.com/vp/products/"):
            raise TypeError
        
        price = text_safety(self.bs.find("span", {"class": "total-price"}))
        
        if price == '':
            return None
        
        price = price.replace(',','')
        price = price.replace('원','')
        
        check.check().is_startswith(self.url, "https://www.coupang.com/vp/products/")

        item = self.bs.find("div", {"class": "prod-atf"})
        
        price = item.find("span", {"class": "total-price"}).get_text(strip=True)
        price = price.replace(',', '')
        price = price.replace('원', '')

        price = int(price)

        return {'price': price}

if __name__ == "__main__":
    parser = Parser("https://www.coupang.com/vp/products/286438028")
    print(parser.get_item_detail())
