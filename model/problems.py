from utils import mysql_config
from utils.logger import Logger
from utils.mysql_config import MySQLConnection

class Problems:
    def __init__(self):
        self.cursor = mysql_config.MySQLConnection().get_cursor()

    def get_problem_id_by_problem_name(self,problem_name):
        self.cursor.execute("select problem_id from problems where problem_name=%s",(problem_name,))
        result = self.cursor.fetchone()
        if result is not None:
            Logger().get_logger().info(result[0])
            return result[0]
        else:
            Logger().get_logger().info(f"problems 没有对应的 {problem_name}")
            return None

    def get_problem_id_by_link(self,link):
        self.cursor.execute("select problem_id from problems where link=%s",(link,))
        result = self.cursor.fetchone()
        if result is not None:
            Logger().get_logger().info(result[0])
            return result[0]
        else:
            Logger().get_logger().info(f"problems 没有对应的 {link}")
            return None
    def get_problem_id(self,link,user_id):
        self.cursor.execute("select problem_id from problems where link=%s and user_id=%s",(link,user_id))
        result = self.cursor.fetchone()
        if result is not None:
            Logger().get_logger().info(result[0])
            return result[0]
        else:
            Logger().get_logger().info(f"problems 没有对应的 {link},{user_id}")
            return None

    def create_problems(self,problems,user_id):
        problems_id_list = []
        for problem in problems:
            problem_id = self.get_problem_id(problem['link'],user_id)
            if problem_id is None:
                self.cursor.execute("insert into problems (problem_name,link,difficulty,user_id) values (%s,%s,%s,%s)", (problem['name'],problem['link'],problem['difficulty'],user_id))
                Logger().get_logger().info(f"插入数据 {problem} - {user_id}")
                MySQLConnection().get_connection().commit()
            problem_id = self.get_problem_id(problem['link'], user_id)
            problems_id_list.append(problem_id)
        return problems_id_list
