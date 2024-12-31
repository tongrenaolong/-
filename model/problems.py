from utils import mysql_config
from utils.logger import Logger
from utils.mysql_config import MySQLConnection

# problems_index = 0
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

    def create_problems(self,problems_list,user_id):
        problems_id_list = []
        try:
            for problem in problems_list:
                problem_id = self.get_problem_id(problem['link'],user_id) # 判断题是否存在
                if problem_id is None:
                    self.cursor.execute("insert into problems (problem_name,link,difficulty,user_id) values (%s,%s,%s,%s)", (problem['name'],problem['link'],problem['difficulty'],user_id))
                    problems_id_list.append(self.cursor.lastrowid)
                    Logger().get_logger().info(f"插入数据 {problem} - {user_id}")
            return problems_id_list
        except Exception as e:
            Logger().get_logger().error(f'{user_id}:{problems_list} 创建失败; {e}')
            raise e

    def get_problems_info_list(self,problems_id_list):
        problems_info_list = []
        for problem_id in problems_id_list:
            self.cursor.execute('select * from problems where problem_id =%s',(problem_id,))
            result = self.cursor.fetchone()
            if result is not None:
                print("result.type(): ",type(result))
                print("result: ",result)
                problems_info_list.append(list(result))
        return problems_info_list

    def problems_info_list_map(self, problems_info_list):
        problems_info_list_map = []
        for problem_info in problems_info_list:
            info_map = dict()
            info_map['problem_id'] = problem_info[0]
            info_map['problem_name'] = problem_info[1]
            info_map['link'] = problem_info[2]
            info_map['upload_time'] = problem_info[3]
            info_map['difficulty'] = problem_info[4]
            info_map['user_id'] = problem_info[5]
            problems_info_list_map.append(info_map)
        return problems_info_list_map

    def delete_problems_id_list(self, problems_id_list):
        try:
            for problem_id in problems_id_list:
                self.cursor.execute('delete from problems where problem_id=%s',(problem_id,))
        except Exception as e:
            Logger().get_logger().error(f'{problems_id_list} 删除失败')
            raise e
