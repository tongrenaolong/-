import hashlib
from flask import jsonify
from utils import mysql_config
from utils.logger import Logger
from utils.User import User

class Quiz:
    # {'title': 'asdf', 'questions': [{'name': 'adf', 'link': 'asdf', 'difficulty': 'easy'}]}
    # const
    # quizData = {
    #                title: title,
    #                description: description, // 添加描述字段
    # questions: questions // 如果没有题目，这里将为空数组
    # };
    def __get_user_id(self,account):
        user_id = User().get_userid_by_account(account)
        if user_id:
            return user_id
        else:
            Logger().get_logger().info(f"{account} is none")

    def __check_problem(self,set_name,link):

        return False

    def create(self,user_info,data):
        self.cursor = mysql_config.MySQLConnection().get_cursor()
        self.__create_set(data['title'],data['description']) # 创建题单
        user_id = self.__get_user_id(user_info['account'])
        for question in data['questions']:
            # 创建上传的问题
            # 不能对上传的题目进行检测，需要人为进行删除；但是可以通过 link 进行基本的检测
            check_ret = self.__check_problem(data['title'],question['link'])
            if check_ret == False:
                self.__create_problem(question['name'],question['link'],question['description'],user_id)
        pass

    def __create_set(self,set_name,description):
        self.cursor.execute("insert into problem_sets (set_name,description) values(%s,%s)",(set_name,description))
        self.cursor.connection.commit()

    def __create_problem(self,problem_name,link,difficulty,user_id):
        self.cursor.execute("insert into problems (problem_name,link,difficulty,user_id) values(%s,%s)",(problem_name,link,difficulty,user_id))
        self.cursor.connection.commit()