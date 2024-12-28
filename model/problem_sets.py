import hashlib
from flask import jsonify

from model.User import User
from utils import mysql_config
from utils.logger import Logger
from model.user_subscriptions import UserSubscriptions
from utils.mysql_config import MySQLConnection
from model.problems import Problems
from model.problem_set_problems import ProblemSetProblems
from model.user_problem_status import UserProblemStatus

class ProblemSets:
    def __init__(self):
        self.cursor = mysql_config.MySQLConnection().get_cursor()

    def get_set_id(self,set_name):
        self.cursor.execute("select set_id from problem_sets where set_name=%s",(set_name))
        result = self.cursor.fetchone()
        if result is not None:
            Logger().get_logger().info(result[0])
            return result[0]
        else:
            Logger().get_logger().info(f"problem_sets 没有对应的 {set_name}")
            return None

    def check_set_exist(self,user_info,data):
        # 在 problem_sets 中通过 set_name 找 set_id
        set_id = self.get_set_id(data['title'])
        # 在 users 中通过 account 找 user_id
        user_id = User().get_user_id(user_info['account'])
        # 在 user_subscriptions 中通过 set_id 和 user_id 判断是否存在用户和题单的对应关系
        if set_id is None:
            return False
        user_subscriptions_exist = UserSubscriptions().check_exist(set_id,user_id)
        if user_subscriptions_exist is False:
            return False
        return True

    def create(self,user_info,data):
        # 检测题单是否存在
        check_exist = self.check_set_exist(user_info,data)
        if check_exist:
            Logger().get_logger().info(f"{data['title']} already exists")
            return jsonify({'status_code':False,'message':'题单已经存在'})
        else:
            Logger().get_logger().info(f"{data['title']} 不存在")
            # 在 problems_sets 中创建题单，获取 set_id
            self.cursor.execute("insert into problem_sets (set_name,description) values(%s,%s)",(data['title'],data['description']))
            MySQLConnection().get_connection().commit()
            set_id = self.get_set_id(data['title'])
            # 在 users 中获取 user_id
            user_id = User().get_user_id(user_info['account'])
            # 在 user_subscriptions 中设置 set_id,user_id
            UserSubscriptions().create(set_id,user_id)
            # 在 problems 中创建题目，并获取 problem_id
            problems_id_list = Problems().create_problems(data['questions'],user_id)
            # 在 problem_set_problems 中设置 set_id,problem_id
            print("set_id: ",set_id)
            print("problems_id_list: ",problems_id_list)
            ProblemSetProblems().insert_problems(set_id,problems_id_list)
            UserProblemStatus().create(user_id, problems_id_list)


    def get_set_except_set_id_list(self,set_id_list):
        set_except_id_list = []
        for set_id in set_id_list:
            self.cursor.execute("select set_id,created_at,description from problem_sets where set_id=%s",(set_id,))
            result = self.cursor.fetchall()
            if result is not None:
                set_except_id_list.append(result)
        return set_except_id_list

    def get_problem_sets_list(self,set_id_list):
        problem_sets_list = []
        for set_id in set_id_list:
            self.cursor.execute("select * from problem_sets where set_id=%s",(set_id,))
            result = self.cursor.fetchall()
            if result is not None:
                # print("result: ",result[0])
                problem_sets_list.append(result[0])
        return problem_sets_list

    def check_problem_sets_exist(self,set_id):
        self.cursor.execute('select * from problem_sets where set_id=%s',(set_id))
        result = self.cursor
        if result is not None:
            return True
        else:
            return False



