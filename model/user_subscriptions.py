import hashlib
from flask import jsonify
from utils import mysql_config
from utils.logger import Logger
from utils.mysql_config import MySQLConnection


class UserSubscriptions:
    def __init__(self):
        self.cursor = mysql_config.MySQLConnection().get_cursor()

    def check_exist(self,set_id,user_id):
        print(f"set_id: {set_id}, user_id: {user_id}")
        self.cursor.execute("select * from user_subscriptions where set_id=%s and user_id=%s", (set_id,user_id))
        result = self.cursor.fetchone()
        if result is not None:
            Logger().get_logger().info(f"找到 {set_id} - {user_id}")
            return True
        else:
            Logger().get_logger().info(f"没有找到 {set_id} - {user_id}")
            return False

    def check_exist_authority(self,set_id,user_id, authority):
        print(f"set_id: {set_id}, user_id: {user_id}, authority: {authority}")
        self.cursor.execute("select * from user_subscriptions where set_id=%s and user_id=%s and authority=%s", (set_id,user_id,authority))
        result = self.cursor.fetchone()
        if result is not None:
            Logger().get_logger().info(f"找到 {set_id} - {user_id}")
            return True
        else:
            Logger().get_logger().info(f"没有找到 {set_id} - {user_id}")
            return False

    def create(self,set_id,user_id,authority):
        print(f'set_id: {set_id}, user_id: {user_id}, authority: {authority}')
        try:
            self.cursor.execute("insert into user_subscriptions (user_id,set_id,authority) values (%s,%s,%s)",(user_id,set_id,authority))
        except Exception as e:
            Logger().get_logger().error(e)
            Logger().get_logger().error(f'{set_id}:{user_id}:{authority} 创建失败')
            raise e
        # MySQLConnection().get_connection().commit()

    def get_set_except_user_id_list(self,user_id):
        set_except_user_id_list = []
        self.cursor.execute("select set_id,authority from user_subscriptions where user_id=%s",(user_id))
        result = self.cursor.fetchall()
        if result is not None:
            for except_user_id in result:
                set_except_user_id_list.append(except_user_id)
        return set_except_user_id_list

    def get_set_id_list(self,user_id):
        set_except_user_id_list = self.get_set_except_user_id_list(user_id)
        set_id_list = []
        print(type(set_except_user_id_list))
        for except_user_id in set_except_user_id_list:
            print(except_user_id)
            set_id_list.append(except_user_id[0])
        return set_id_list

    def delete_set_id(self,set_id):
        try:
            self.cursor.execute('delete from user_subscriptions where set_id=%s', (set_id))
        except Exception as e:
            Logger().get_logger().error(f'{set_id} 删除失败')
            raise e

    def get_user_id_list(self,set_id_list):
        user_id_list = []
        for set_id in set_id_list:
            self.cursor.execute('select user_id from user_subscriptions where set_id=%s and authority=1',(set_id))
            result = self.cursor.fetchone()
            if result is not None:
                user_id_list.append(result[0])
        return user_id_list

    def count_member(self,set_id):
        self.cursor.execute('select count(*) from user_subscriptions where set_id=%s',(set_id))
        result = self.cursor.fetchone()
        if result is not None:
            return result[0]
        else:
            return 0

    def delete_info(self,user_id,set_id):
        try:
            self.cursor.execute('delete from user_subscriptions where user_id=%s and set_id=%s', (user_id, set_id))
        except Exception as e:
            Logger().get_logger().error(f'{user_id}:{set_id} 删除失败')
            raise e