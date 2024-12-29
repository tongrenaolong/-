import hashlib
from flask import jsonify
from utils import mysql_config
from utils.logger import Logger
from utils.mysql_config import MySQLConnection


class UserProblemStatus:
    def __init__(self):
        self.cursor = mysql_config.MySQLConnection().get_cursor()

    def get_user_problem_status_list(self,problem_id_list):
        status_list = []
        for problem_id in problem_id_list:
            tem = []
            self.cursor.execute('select count(*) from user_problem_status where problem_id=%s',(problem_id,))
            result = self.cursor.fetchone()
            if result is not None:
                print("result: ",result)
                tem.append(result[0])
            self.cursor.execute('select count(*) from user_problem_status where problem_id=%s and status="completed"',(problem_id,))
            result = self.cursor.fetchone()
            if result is not None:
                print("result: ",result)
                tem.append(result[0])
            status_list.append(tem)
        return status_list

    def get_user_problem_status(self,user_id,problem_id_list):
        user_problem_status = []
        for problem_id in problem_id_list:
            print(user_id,problem_id)
            self.cursor.execute('select status from user_problem_status where user_id=%s and problem_id=%s',(user_id,problem_id))
            result = self.cursor.fetchone()
            if result is not None:
                user_problem_status.append(result[0])
            else:
                print("get_user_problem_status None")
        return user_problem_status

    def create(self,user_id, problems_id_list):
        for problem_id in problems_id_list:
            self.cursor.execute('insert into user_problem_status (user_id, problem_id) values (%s, %s)',(user_id,problem_id))
            MySQLConnection().get_connection().commit()

    def delete_problems_id_list(self,problems_id_list):
        for problem_id in problems_id_list:
            self.cursor.execute('delete from user_problem_status where problem_id=%s',(problem_id))
        MySQLConnection().get_connection().commit()

    def refreshStatus(self,user_id, problem_id,status, input_text, image_data):
        self.cursor.execute('update user_problem_status set status=%s,description=%s,image=%s where user_id=%s and problem_id=%s',(status,input_text,image_data,user_id,problem_id))
        MySQLConnection().get_connection().commit()
