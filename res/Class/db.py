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

# 

# 알람 테이블
class AlarmTable:
    #테이블을 만든다, 자세한 내용은 알람 조건 설정 정한 후 생각해봐야 될듯
    def create_table(self):
        sql = sql_text("""
                       CREATE TABLE price_alarm (
                           `guild_id` bigint unsigned,
                           `channel_id` bigint unsigned,
                           `author_id` bigint unsigned,
                           `product_id` int unsigned,
                           `product_value` int unsigned
                           );
                       """)

        try:
            self.connection.execute(sql)
        except:
            error_message = "Already exist"
            print(error_message)

    #전체 테이블을 불러온다.
    def read_all(self):
        #실행
        sql = sql_text("""
                       SELECT *
                       FROM `price_alarm`
                       """)
        df = pandas.read_sql_query(sql = sql, con = self.connection)

        return df
    
    #저장한다.
    def insert(self, guild_id, channel_id, author_id, product_id, product_value):
        sql = sql_text("""
                       INSERT INTO `price_alarm`
                       VALUES (:guild_id, :channel_id, :author_id, :product_id, :product_value)
                       """)
    
        self.connection.execute(sql, guild_id=guild_id, channel_id=channel_id, author_id=author_id, product_id=product_id, product_value=product_value)
    
    

