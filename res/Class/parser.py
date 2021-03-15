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
    def get_items(self, input_count = 3, is_include_ads = False):
        # 아이템 그룹 파싱해옴
        items_group = self.bs.find("ul", {"id": "productList"}).find_all("li")
        
        # 파싱해온 그룹에서 count 갯수만큼 뽑음, 광고 제거는 선택
        items_list = []
        item_count = 0
        for item in items_group:
            if ('search-product__ad-badge' not in item.get("class")) or is_include_ads:
                items_list.append(item)
                item_count += 1
                print(item_count)
            if item_count >= input_count:
                break
            
        # 정보 뽑아 output 사전에 저장한다.
        for item in items_list:
            name = item.find("dd", {"class": "descriptions"}).find("div", {"class": "name"}).text
            image_url = "https:%s" % item.find("dt", {"class": "image"}).find("img").get("src")
            output = {"name" : name, "image_url" : image_url
                }
            
        return output


if __name__ == "__main__":
    parser=parser("https://www.coupang.com/np/search?component=&q=%EA%B2%80%EC%83%89&channel=user")
    parser.get_items(1)
