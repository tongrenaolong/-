from model.User import User
from utils import mysql_config
from utils.logger import Logger
from model.user_subscriptions import UserSubscriptions

class ProblemSets:
    def __init__(self):
        self.cursor = mysql_config.MySQLConnection().get_cursor()

    def get_set_id_list(self,set_name):
        set_id_list = []
        self.cursor.execute("select set_id from problem_sets where set_name=%s",(set_name))
        result = self.cursor.fetchall()
        Logger().get_logger().info(result)
        for set_id_tuple in result:
            set_id_list.append(set_id_tuple[0])
        else:
            Logger().get_logger().info(f"problem_sets 没有对应的 {set_name}")
        return set_id_list

    def get_set_id(self,user_id,set_name):
        # 保证一个用户的所有题集不重名
        set_id_list = self.get_set_id_list(set_name)
        print("set_id_list: ",set_id_list)
        for set_id in set_id_list:
            self.cursor.execute('select * from user_subscriptions where user_id=%s and set_id=%s',(user_id,set_id))
            result = self.cursor.fetchone()
            if result is not None:
                return result[0]
        return None

    def check_set_exist(self,user_info,set_data):
        # 不论如何都是正确的
        # 在 problem_sets 中通过 set_name 找 set_id
        set_id_list = self.get_set_id_list(set_data['title'])
        # 在 users 中通过 account 找 user_id
        user_id = User().get_user_id(user_info['account'])
        # 在 user_subscriptions 中通过 set_id 和 user_id 判断是否存在用户和题单的对应关系
        for set_id in set_id_list:
            user_subscriptions_exist = UserSubscriptions().check_exist(set_id,user_id)
            if user_subscriptions_exist:
                return True
        return False

    def create_problem_set(self,set_name,description):
        try:
            # 在创建阶段保证一个 user 创建的题单不能重名
            self.cursor.execute("insert into problem_sets (set_name,description) values(%s,%s)",(set_name, description))
        except Exception as e:
            Logger().get_logger().error(f':{set_name}:{description} 创建失败')
            raise e

    def get_last_set_id(self,set_name):
        self.cursor.execute('select set_id from problem_sets where set_name=%s order by set_id desc limit 1',(set_name))
        result = self.cursor.fetchone()
        if result is not None:
            return result[0]
        return None

    def get_last_set_id_test(self):
        return self.cursor.lastrowid

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
        print('set_id_list: ',set_id_list)
        for set_id in set_id_list:
            self.cursor.execute("select * from problem_sets where set_id=%s",(set_id,))
            result = self.cursor.fetchall()
            if result is not None:
                # print("result: ",result[0])
                problem_sets_list.append(list(result[0]))
        return problem_sets_list

    def get_problem_sets_list_by_name(self,set_name):
        problem_sets_list = []
        print(set_name)
        self.cursor.execute("select * from problem_sets where set_name=%s",(set_name,))
        result = self.cursor.fetchall()
        if result is not None:
            print(result)
            problem_sets_list.append(list(result[0]))
        return problem_sets_list

    def check_problem_sets_exist(self,set_id):
        self.cursor.execute('select * from problem_sets where set_id=%s',(set_id))
        result = self.cursor
        if result is not None:
            return True
        else:
            return False

    def delete_set_id(self,set_id):
        try:
            self.cursor.execute('delete from problem_sets where set_id=%s', (set_id))
        except Exception as e:
            Logger().get_logger().error(f'{set_id} 删除失败')
            raise e


