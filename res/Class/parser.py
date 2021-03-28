import bs4
import requests

class parser:
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

    def get_items(self, limit=3, is_except_ads=True):
        #에러 처리
        if not self.url.startswith("https://www.coupang.com/np/search?component=&q="):
            raise TypeError

        assert isinstance(limit, int), "limit은 정수여야합니다."
        assert limit >= 0, "limit은 0보다 커야합니다."
        
        items_page = self.bs.find("ul", {"id": "productList"})
        if items_page is None:
            return None
        else:
            items_group = self.bs.find("ul", {"id": "productList"}).find_all("li")
        
        # 파싱해온 그룹에서 count 갯수만큼 뽑음, 광고 제거는 선택
        items_list = []
        item_count = 0
        for item in items_group:
            if ('search-product__ad-badge' not in item.get("class")) or is_except_ads:
                items_list.append(item)
                item_count += 1
            if item_count >= limit:
                break
        
        # 정보 뽑아 output 사전에 저장한다.
        datas = []
        def text_safety(bs):
            if not bs:
                return ""
            else:
                return bs.text
            
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

if __name__ == "__main__":
    parser = parser("https://www.coupang.com/np/search?component=&q=%EA%B2%80%EC%83%89&channel=user")
    print(parser.get_items(1))
