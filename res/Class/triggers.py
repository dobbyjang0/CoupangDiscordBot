from . import db

class alarm:
    def __init__(self, bot):
        self.bot = bot

    async def proccess(self):
        scan_table = db.ScanTable()
        record_table = db.SaleRecordTable()
        alarm_table = db.PriceAlarmTable()
        
        # 스캔 대상 제품 스캔
        scan_df = scan_table.read_all()
        for idx in scan_df.index:
            product_id = scan_df.at[idx, 0]
            latest_price = scan_df.at[idx, 1]
            
            # 현재 가격 스캔, 나중에 파셔쪽에서 클래스 분리, 함수화 시키기
            url = "https://www.coupang.com/vp/products/%s" % product_id
            cou_parser = parser.parser(url)
            now_price = cou_parser.get_item_detail()['price']
            
            if now_price != latest_price:
                record_table.insert(product_id, now_price)
                scan_table.update(product_id, now_price)
        
        #알람 보낸다.
        alarm_df = alarm_table.read_today()
        for idx in alarm_df.index:
            channel_id = int(alarm_df[idx, 1])
            product_id = alarm_df[idx, 3]
            price = alarm_df[idx, 4]
            
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send(f"제품코드 {product_id} 가격 {price}로 변동됨")
