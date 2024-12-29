import hashlib
from flask import jsonify
from utils import mysql_config
from utils.logger import Logger


class User:
    def __init__(self):
        self.cursor = mysql_config.MySQLConnection().get_cursor()

    def login(self,data):
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
            ret = self.cursor.execute("insert into users (account,username,password)  values(%s,%s,%s)",(data['account'],data['username'],password))

            mysql_config.MySQLConnection().get_connection().commit()
        except Exception as e:
            Logger().get_logger().info(e)
            mysql_config.MySQLConnection().get_connection().rollback()
            ret = 0
        if ret >0:
            Logger().get_logger().info(f"{data['account']} 插入成功")
            return jsonify({'status_code': True, 'message': '注册成功', 'account': data['account']})
        else:
            Logger().get_logger().info(f"{data['account']} 插入失败")
            return jsonify({'status_code': False, 'message': '注册失败', 'account': data['account']})

    def get_user_id(self,account):
        self.cursor.execute("select * from users where account=%s",(account))
        result = self.cursor.fetchone()
        if result is not None:
            Logger().get_logger().info(result[0])
            return result[0]
        else:
            Logger().get_logger().info(f"没有找到 {account}")
            return None


