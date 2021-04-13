import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import text as sql_text
import pymysql
import pandas

#싱글톤 커낵션
class Connection():
    def __new__(cls):
        if not hasattr(cls, 'cursor'):

            def conn(user, password, host, port, db, charset):
                db_connection_str = f'mysql+pymysql://{user}:{password}@{host}:{port}/{db}'
                engine = create_engine(db_connection_str, encoding = charset, echo = True)

                return engine

            def quick_admin_login():
                context = pandas.read_csv('admin_login_info.csv', header=None, index_col=0, squeeze=True).to_dict()
                connection = conn(**context)
                print(connection)

                return connection

            cls.cursor = quick_admin_login()

        return cls.cursor

#부모 테이블 클래스, 여기다가 각 테이블마다 추가되는거 상속해서 추가하기
class Table:
    def __init__(self):
        self.connection = Connection()
        #self.name 필요하려나?

# 스캔할 제품 테이블
# create_table, insert, read_by_id, read_all, update, delete
class ScanTable(Table):
    def create_table(self):
        sql = sql_text("""
                       CREATE TABLE `scan_product` (
                           `product_id` int unsigned PRIMARY KEY,
                           `latest_price` int unsigned
                           );
                       """)

        try:
            self.connection.execute(sql)
        except:
            error_message = "Already exist"
            print(error_message)
            
    #값을 넣는다. 초기에 알림 신청할 때 없다면 넣어주자
    def insert(self, product_id, latest_price):
        sql = sql_text("""
                       INSERT INTO `scan_product`
                       VALUES (:product_id, :latest_price)
                       """)
        
        self.connection.execute(sql, product_id=product_id, latest_price=latest_price)
    
    # id를 넣으면 가격을 확인한다. 알림 신청할 때 값 있는지 확인용? (없으면 None값이 나온다.)
    def read_by_id(self, product_id):
        sql = sql_text("""
                       SELECT latest_price
                       FROM `scan_product`
                       WHERE product_id = :product_id
                       """)
    
        result = self.connection.execute(sql, product_id=product_id).fetchone()
        
        return result
    
    # 모든 값을 불러온다. 가격 업데이트된거 있나 스캔할 때 이걸로 반복문 돌릴 것
    def read_all(self):
        sql = sql_text("""
                       SELECT *
                       FROM `scan_product`
                       """)
    
        df = pandas.read_sql_query(sql = sql, con = self.connection)
        
        return df
    
    # id를 입력하면 값을 수정할 수 있다. 가격 변동이 일어났으면 시계열 데이터 추가와 함께 할 것
    def update(self, product_id, latest_price):
        sql = sql_text("""
                       UPDATE `scan_product`
                       SET latest_price = :latest_price
                       WHERE product_id = :product_id;
                       """)
    
        self.connection.execute(sql, product_id=product_id, latest_price=latest_price)
    
    # 스캔 제품에서 제외시킨다.
    def delete(self, product_id):
        sql = sql_text("""
                       DELETE FROM `scan_product`
                       where product_id = :product_id
                       """)
    
        self.connection.execute(sql, product_id=product_id)
    
# 시계열 가격 데이터 테이블
# create_table, inset, read_all, read_by_id
class SaleRecordTable(Table):
    # 테이블을 만든다.
    def create_table(self):
        sql = sql_text("""
                       CREATE TABLE `sale_record`(
                           `time` timestamp DEFAULT NOW(),
                           `product_id` int unsigned FOREIGN KEY REFERENCES `products`,
                           `price` int unsigned
                           );
                       """)

        try:
            self.connection.execute(sql)
        except:
            error_message = "Already exist"
            print(error_message)
    
    #값을 하나 추가한다. 가격 변동이 일어날때 저장할 것
    def insert(self, product_id, price):
        sql = sql_text("""
                       INSERT INTO `sale_record`
                       VALUES (default, :product_id, :price)
                       """)
                     
        self.connection.execute(sql, product_id=product_id, price=price)  

    #로그 폴더이므로,update나 delete는 만들어두지 않았음.
    #필요하면 용도에 따라 만듬
    
    #모든 값을 읽는다.
    def read_all(self):
        sql = sql_text("""
                       SELECT *
                       FROM `sale_record`
                       ORDER BY product_id
                       """)
        
        # 귀찮아서 걍 판다스로 뽑음
        df = pandas.read_sql_query(sql = sql, con = self.connection)
        
        return df
    
    #id를 넣으면 날짜와 가격을 뽑는다.
    def read_by_id(self, product_id):
        sql = sql_text("""
                       SELECT time, price
                       FROM `sale_record`
                       WHERE product_id = :product_id
                       ORDER BY time
                       """)
        
        df = pandas.read_sql_query(sql = sql, con = self.connection, params={"product_id":product_id})
        
        return df

# 알람 테이블
#create_table insert read_by_user read_today read_by_user read_all update delete_by_id delete_by_channel
class PriceAlarmTable(Table):
    #테이블을 만든다. 길드 아이디는 저장할필요 없을 듯?
    def create_table(self):
        sql = sql_text("""
                       CREATE TABLE price_alarm (
                           `guild_id` bigint unsigned,
                           `channel_id` bigint unsigned,
                           `author_id` bigint unsigned,
                           `product_id` int unsigned FOREIGN KEY REFERENCES `products`,
                           `product_price` int unsigned
                           );
                       """)

        try:
            self.connection.execute(sql)
        except:
            error_message = "Already exist"
            print(error_message)

    #저장한다. 알람신청할 때 꼭 실행시켜주자
    def insert(self, guild_id, channel_id, author_id, product_id, product_value):
        sql = sql_text("""
                       INSERT INTO `price_alarm`
                       VALUES (:guild_id, :channel_id, :author_id, :product_id, :product_price)
                       """)
    
        self.connection.execute(sql, guild_id=guild_id, channel_id=channel_id, author_id=author_id, product_id=product_id, product_value=product_value)
    
    # 신청한 사람에 따라서 불러온다.
    def read_by_user(self, author_id):
        sql = sql_text("""
                       SELECT guild_id, channel_id, product_id, product_price
                       FROM `price_alarm`
                       WHERE author_id = :author_id
                       """)
        df = pandas.read_sql_query(sql=sql, con=self.connection, params={"author_id": author_id})
        
        return df
    
    #오늘 변경된 (알림 보내야할) 목록을 뽑아온다.
    def read_today(self):
        sql = sql_text("""
                       SELECT pa.guild_id, pa.channel_id, pa.author_id, pa.product_id, sr.price
                       FROM (
                           SELECT product_id, price
                           FROM `sale_record`
                           WHERE TIMESTAMPDIFF(DAY, time, CURRENT_TIMESTAMP) < 1
                           ) AS sr
                       JOIN `price_alarm` AS pa ON pa.product_id = sr.product_id 
                       WHERE sr.price <= pa.product_price
                       """)
                       
        df = pandas.read_sql_query(sql = sql, con = self.connection)

        return df
    
    #전체 테이블을 불러온다. (잘 안 쓰일듯)
    def read_all(self):
        #실행
        sql = sql_text("""
                       SELECT *
                       FROM `price_alarm`
                       """)
        df = pandas.read_sql_query(sql = sql, con = self.connection)

        return df
    
    #기준 가격을 업데이트?
    def update(self, guild_id, channel_id, author_id, product_id, product_value):
        sql = sql_text("""
                       UPDATE `price_alarm`
                       SET product_value = :product_value
                       WHERE guild_id=:guild_id, channel_id=:channel_id, author_id=:author_id, product_id=:product_id
                       """)
    
        self.connection.execute(sql, guild_id=guild_id, channel_id=channel_id, author_id=author_id, product_id=product_id, product_value=product_value)
    
    #삭제한다. 조건은 좀 생각해봐야 될 듯
    def delete_by_id(self, author_id, product_id):
        sql = sql_text("""
                       DELETE FROM `price_alarm`
                       WHERE author_id=:author_id, product_id=:product_id
                       """)
    
        self.connection.execute(sql, author_id=author_id, product_id=product_id)
        
    def delete_by_channel(self, channel_id, author_id):
        sql = sql_text("""
                       DELETE FROM `price_alarm`
                       WHERE channel_id=:channel_id, author_id=:author_id
                       """)
    
        self.connection.execute(sql, channel_id=channel_id, author_id=author_id)
    
#main 함수
def main():
    pass

if __name__ == "__main__":
    main()
