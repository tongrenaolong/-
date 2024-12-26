import hashlib
from flask import jsonify
from utils import mysql_config
from utils.logger import Logger


class ProblemSetProblems:
    def __init__(self):
        self.cursor = mysql_config.MySQLConnection().get_cursor()

    def check_exist(self,set_id,problem_id):
        self.cursor.execute("select * from problem_set_problems where set_id=%s and problem_id=%s",(set_id,problem_id))
        result = self.cursor.fetchone()
        if result is not None:
            Logger().get_logger().info(f"找到 {set_id} - {problem_id}")
            return True
        else:
            Logger().get_logger().info(f"没有找到 {set_id} - {problem_id}")
            return False

    def insert_problems(self,set_id,problems_id_list):
        for problem_id in problems_id_list:
            self.cursor.execute("insert into problem_set_problems (set_id,problem_id) values(%s,%s)",(set_id,problem_id))
            Logger().get_logger().info(f"insert into {set_id},{problem_id}")

