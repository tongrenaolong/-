import hashlib
from flask import jsonify
from utils import mysql_config
from utils.logger import Logger


class User:
    def __init__(self):
        self.cursor = mysql_config.MySQLConnection().get_cursor()

    def login(self,data):
        print('data: ',data)
        if data is None:
            return jsonify({'status_code': False, 'message': '请先登录'})
        password = hashlib.md5(data['password'].encode()).hexdigest()
        Logger().get_logger().info(f"account: {data['account']}, password: {password}")

        self.cursor.execute("select * from users where account=%s and password=%s",(data['account'],password,))

        # 获取查询结果
        result = self.cursor.fetchone()
        print(result)
        if result:
            print("Login successful!")
            return jsonify({'status_code': True, 'message': '登录成功', 'account': data['account']})
        else:
            print("Invalid username or password.")
            return jsonify({'status_code': False, 'message': '登录失败', 'account': data['account']})

    def register(self,data):
        password = hashlib.md5(data['password'].encode()).hexdigest()
        Logger().get_logger().info(f"account: {data['account']}, username: {data['username']}, password: {password}")
        try:
            mysql_config.MySQLConnection().get_connection().begin()
            self.cursor.execute("insert into users (account,username,password)  values(%s,%s,%s)",(data['account'],data['username'],password))

            mysql_config.MySQLConnection().get_connection().commit()
        except Exception as e:
            Logger().get_logger().error(e)
            mysql_config.MySQLConnection().get_connection().rollback()
            raise e

    def get_user_id(self,account):
        self.cursor.execute("select * from users where account=%s",(account))
        result = self.cursor.fetchone()
        if result is not None:
            Logger().get_logger().info(result[0])
            return result[0]
        else:
            Logger().get_logger().info(f"没有找到 {account}")
            return None

    def get_account(self,user_id):
        self.cursor.execute('select account from users where user_id=%s',(user_id))
        result = self.cursor.fetchone()
        if result is not None:
            return result[0]
        else:
            return None

