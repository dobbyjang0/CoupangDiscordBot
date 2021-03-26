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

class AlramTable:
    #테이블을 만든다, 자세한 내용은 알람 조건 설정 정한 후 생각해봐야 될듯
    def create_table(self):
        sql = sql_text("""
                       CREATE TABLE alarm_table (
                           `index` int unsigned PRIMARY KEY AUTO_INCREMENT,
                           `time` datetime DEFAULT NOW(),
                           `type` varchar(15),
                           `type_sub` varchar(15),
                           `guild_id` bigint unsigned,
                           `channel_id` bigint unsigned,
                           `author_id` bigint unsigned,
                           `product_code` varchar(15)
                           );
                       """)

        print(self.connection)
        try:
            self.connection.execute(sql)
        except:
            error_message = "Already exist"
            print(error_message)