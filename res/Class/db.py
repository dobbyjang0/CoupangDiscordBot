import pymysql
import aiomysql
import functools

from res.Class import errors

from typing import Union


def connection_handler():

    def wrapper(func):

        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            instance = args[0]

            if hasattr(instance, "session") is False:
                raise errors.InstanceHasNotSession("인스턴스에 session attr이 없습니다.")

            async with instance.session.connection as session:
                async with session.cursor() as cursor:
                    session: aiomysql.connection.Connection = session
                    cursor: aiomysql.cursors.Cursor = cursor

                    return await func(instance, session, cursor, *args[1:], **kwargs)

        return wrapped

    return wrapper


class DatabaseSession:

    def __init__(
            self,
            host: str,
            user: str,
            port: int,
            database: str = None,
            db: str = None,
            password: str = None,
            passwd: str = None
    ):

        self._database = database or db
        self._host = host
        self._user = user
        self._password = password or passwd
        self._port = port

    @property
    def database(self):
        return self._database

    @database.setter
    def database(self, value):
        self._database = value

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value

    @property
    def user(self):
        return self._user

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    passwd = password

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value

    @property
    def connection(self):
        return aiomysql.connect(
            host=self.host, port=self.port, user=self.user, password=self.password, db=self.database
        )


class Database:

    def __init__(
            self,
            database: str = None,
            db: str = None,
            host: str = "localhost",
            user: str = "root",
            password: str = "password",
            passwd: str = None,
            port: int = 3306
    ):

        if not database and not db:
            raise Exception("database 또는 db가 충족되어야합니다.")

        self.session = DatabaseSession(
            database=database or db,
            host=host,
            user=user,
            password=passwd or password,
            port=port
        )


class ScanTable(Database):

    def __init__(self):
        super().__init__("")

    @connection_handler()
    async def create_table(self, session, cursor):
        sql = """
        CREATE TABLE `scan_product` (
            `product_id` bigint unsigned PRIMARY KEY,
            `latest_price` int unsigned
        )
        """

        await cursor.execute(sql)
        await session.commit()

    @connection_handler()
    async def insert(self, session, cursor, product_id, latest_price):
        sql = """
        INSERT INTO `scan_product` (product_id, latest_price)
        VALUES (%(product_id)s, %(latest_price)s) 
        ON DUPLICATE KEY UPDATE latest_price=%(latest_price)s
        """

        await cursor.execute(sql, {"product_id": product_id, "latest_price": latest_price})
        await session.commit()

    @connection_handler()
    async def read_by_id(self, session, cursor, product_id) -> Union[None, tuple]:
        sql = """
        SELECT latest_price FROM `scan_product`
        WHERE product_id = %s
        """
    
        await cursor.execute(sql, product_id)
        return await cursor.fetchone()

    @connection_handler()
    async def read_all(self, session, cursor):
        sql = "SELECT * FROM `scan_product`"

        await cursor.execute(sql)
        return await cursor.fetchall()
    
    @connection_handler()
    async def update(self, session, cursor, product_id, latest_price):
        sql = """
        UPDATE `scan_product`
        SET latest_price = %s
        WHERE product_id = %s
        """

        await cursor.execute(sql, (latest_price, product_id))
        await session.commit()

    @connection_handler()
    async def delete(self, session, cursor, product_id):
        sql = "DELETE FROM `scan_product` where product_id = %s"
        await cursor.execute(sql, product_id)
        await session.commit()


# 시계열 가격 데이터 테이블
# create_table, inset, read_all, read_by_id
class SaleRecordTable(Database):

    # 테이블을 만든다.
    @connection_handler()
    async def create_table(self, session, cursor):
        sql = """
        CREATE TABLE `sale_record`(
            `time` timestamp NOT NULL DEFAULT NOW(),
            `product_id` bigint unsigned,
            `price` int unsigned
        )
        """

        await cursor.execute(sql)

        try:
            await session.commit()

        except pymysql.err.InternalError as error:
            code, msg = error.args

            if code == 1050:
                return msg

    @connection_handler()
    async def insert(self, session, cursor, product_id, price):
        sql = """
        INSERT INTO `sale_record`
        VALUES (default, %s, %s)
        """

        await cursor.execute(sql, (product_id, price))
        await session.commit()

    # 로그 폴더이므로,update나 delete는 만들어두지 않았음.
    # 필요하면 용도에 따라 만듬
    # 모든 값을 읽는다.
    @connection_handler()
    async def read_all(self, session, cursor):
        sql = "SELECT * FROM `sale_record` ORDER BY product_id"
        
        # 귀찮아서 걍 판다스로 뽑음
        await cursor.execute(sql)
        results = await cursor.fetchall()

        if not results:
            return None

        return results
    
    # product_id를 넣으면 날짜와 가격을 뽑는다.
    @connection_handler()
    async def read_by_id(self, session, cursor, product_id):
        sql = """
        SELECT time, price FROM `sale_record` 
        WHERE product_id = :product_id ORDER BY time
        """

        await cursor.execute(sql, product_id)
        return await cursor.fetchone()


# 알람 테이블
# create_table insert read_by_user read_today read_by_user read_all update delete_by_id delete_by_channel
class PriceAlarmTable(Table):
    #테이블을 만든다. 길드 아이디는 저장할필요 없을 듯?
    def create_table(self):
        sql = sql_text("""
                       CREATE TABLE price_alarm (
                           `guild_id` bigint unsigned,
                           `channel_id` bigint unsigned,
                           `author_id` bigint unsigned,
                           `product_id` bigint unsigned,
                           `product_price` int unsigned
                           );
                       """)

        try:
            self.connection.execute(sql)
        except:
            error_message = "Already exist"
            print(error_message)

    # 저장한다. 알람신청할 때 꼭 실행시켜주자
    def insert(self, guild_id, channel_id, author_id, product_id, product_price):
        sql = sql_text("""
                       INSERT INTO `price_alarm`
                       VALUES (:guild_id, :channel_id, :author_id, :product_id, :product_price)
                       """)
    
        self.connection.execute(sql, guild_id=guild_id, channel_id=channel_id, author_id=author_id, product_id=product_id, product_price=product_price)
    
    # 가격을 업데이트한다. 사용자가 알람 가격을 바꾸고 싶을 때 실행시키자.
    def update_price(self, channel_id, author_id, product_id: int, product_price: int):
        sql = sql_text("""
                       UPDATE `price_alarm`
                       SET product_price = :product_price
                       WHERE channel_id=:channel_id and author_id = :author_id and product_id = :product_id;
                       """)
    
        self.connection.execute(sql, channel_id=channel_id, author_id=author_id, product_id=product_id, product_price=product_price)
        
        
    # 신청한 사람에 따라서 불러온다.
    def read_by_user(self, author_id):
        sql = sql_text("""
                       SELECT guild_id, channel_id, product_id, product_price
                       FROM `price_alarm`
                       WHERE author_id = :author_id
                       """)
        df = pandas.read_sql_query(sql=sql, con=self.connection, params={"author_id": author_id})
        
        return df
    
    # 오늘 변경된 (알림 보내야할) 목록을 뽑아온다.
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
    
    # 전체 테이블을 불러온다. (잘 안 쓰일듯)
    def read_all(self):
        #실행
        sql = sql_text("""
                       SELECT *
                       FROM `price_alarm`
                       """)
        df = pandas.read_sql_query(sql = sql, con = self.connection)

        return df
    
    # 삭제한다. 조건은 좀 생각해봐야 될 듯
    def delete_by_id(self, author_id, product_id):
        sql = sql_text("""
                       DELETE FROM `price_alarm`
                       WHERE author_id=:author_id and product_id=:product_id
                       """)
    
        self.connection.execute(sql, author_id=author_id, product_id=product_id)
        
    def delete_by_channel(self, channel_id, author_id):
        sql = sql_text("""
                       DELETE FROM `price_alarm`
                       WHERE channel_id=:channel_id and author_id=:author_id
                       """)
    
        self.connection.execute(sql, channel_id=channel_id, author_id=author_id)
    
#main 함수
def main():
    ScanTable().create_table()
    SaleRecordTable().create_table()
    PriceAlarmTable().create_table()
    pass

if __name__ == "__main__":
    main()
