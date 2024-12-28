import datetime
import json

from flask import Flask, render_template, request, make_response, redirect, url_for, jsonify
from model.User import User
from utils.logger import Logger
from utils.mysql_config import MySQLConnection

from model.problem_sets import ProblemSets
from model.user_subscriptions import UserSubscriptions
from model.problem_set_problems import ProblemSetProblems
from model.problems import Problems
from model.user_problem_status import UserProblemStatus

app = Flask(__name__)

def verify_login():
    user_info = request.cookies.get('user_info')
    resp = User().login(json.loads(user_info))
    return resp.get_json().get('status_code')

@app.before_request
def before_request():
    path = request.path
    # 排除公开访问的路径
    if path in ['/register', '/','/login']:
        return

    # 其他路径检查登录状态
    if not verify_login():
        return render_template('error.html',data={"status_code":401,"message":"用户未登录"})

@app.route('/',methods=['GET','POST'])
def index():
    return render_template('home.html')

@app.route('/login',methods=['POST'])
def login():
    user_info = request.get_json()
    Logger().get_logger().info(user_info)
    user = User()
    resp = make_response(user.login(user_info))
    # 设置一个 Cookie（例如，保存用户名）
    resp.set_cookie('user_info', json.dumps(user_info), expires=datetime.datetime.now() + datetime.timedelta(days=1))
    return resp

@app.route('/register',methods=['POST'])
def register():
    data = request.get_json()
    Logger().get_logger().info(data)
    user = User()
    return user.register(data)

@app.route('/main', methods=['GET'])
def main():
    return render_template('main.html')  # 返回 main.html 页面

@app.route('/create_problems', methods=['POST'])
def create_problems():
    user_info_str = request.cookies.get('user_info')
    user_info = json.loads(user_info_str)
    user_id = User().get_user_id(user_info['account'])

    data = request.get_json()
    Problems().create_problems(data['questions'],user_id)
    problems_id_list = []
    for problem in data['questions']:
        problems_id_list.append(Problems().get_problem_id_by_problem_name(problem['name']))
    ProblemSetProblems().insert_problems(data['set_id'],problems_id_list)
    UserProblemStatus().create(user_id,problems_id_list)
    return jsonify({'status':True,'message':'新增题目成功'}),201


@app.route('/create_set', methods=['POST'])
def create_set():
    user_info_str = request.cookies.get('user_info')
    user_info = json.loads(user_info_str)

    data = request.get_json()
    # {'title': 'asdf', 'questions': [{'name': 'adf', 'link': 'asdf', 'difficulty': 'easy'}]}
    print(user_info)
    # Quiz().create(user_info,data)
    ProblemSets().create(user_info,data)
    Logger().get_logger().info('题单创建成功')
    return json.dumps({'status_code': True,'message':'注册题单成功'}),200

@app.route('/get_sets', methods=['GET'])
def get_sets():
    user_info_str = request.cookies.get('user_info')
    user_info = json.loads(user_info_str)
    # 通过 user_info 得到他加入的所有 problem_set
    # 返回 problem_sets
    user_id = User().get_user_id(user_info['account'])
    set_except_user_id_list = UserSubscriptions().get_set_except_user_id_list(user_id)
    set_id_list = UserSubscriptions().get_set_id_list(user_id)
    print("set_id_list: ",set_id_list)
    problem_sets_list = ProblemSets().get_problem_sets_list(set_id_list)
    print("problem_sets_list: ",problem_sets_list)
    print("set_except_user_id_list: ",set_except_user_id_list)
    ret_list = []
    for problem_set in problem_sets_list:
        for set_except_user_id in set_except_user_id_list:
            if set_except_user_id[0] == problem_set[0]:
                tem = [val for val in problem_set]
                tem.append(set_except_user_id[1])
                ret_list.append(tem)
                # print("problem_set_pre: ",problem_set)
                # problem_set.append(set_except_user_id[1])
                # print("problem_set_after: ",problem_set)
    # [[set_name,created_at,description,authority]]
    # print(ret_list)
    # print(problem_sets_list)
    # 将最后返回的元素转成 list
    return jsonify({'status_code':True,'sets':ret_list}),201

@app.route('/get_set_problems',methods=['GET'])
def get_set_problems():
    user_info_str = request.cookies.get('user_info')
    user_info = json.loads(user_info_str)
    user_id = User().get_user_id(user_info['account'])
    # 由于 set_id 是唯一的，只需要通过 set_id 查找就可以了
    set_id = int(request.args.get('set_id', 0))
    print("set_id: ",set_id)
    result = ProblemSets().check_problem_sets_exist(set_id)
    if result is False:
        return jsonify({'status_code':False}),201
    else:
        problems_id_list = ProblemSetProblems().get_problems_list(set_id)
        # 获取每个题的 总人数 和 完成人数
        status_list = UserProblemStatus().get_user_problem_status_list(problems_id_list)
        print("status_list: ",status_list)
        problems_info_list = Problems().get_problems_info_list(problems_id_list)
        problems_info_list_map = Problems().problems_info_list_map(problems_info_list)
        print("problems_info_list_map: ",problems_info_list_map)
        user_problem_status = UserProblemStatus().get_user_problem_status(user_id,problems_id_list)
        print("user_problem_status: ",user_problem_status)
        for i in range(len(problems_info_list_map)):
            problems_info_list_map[i]['all'] = status_list[i][0]
            problems_info_list_map[i]['completed'] = status_list[i][1]
            problems_info_list_map[i]['status'] = user_problem_status[i]

        print("problems_id_list: ",problems_id_list)
        print("problems_info_list: ", problems_info_list)
        print("problems_info_list_map: ", problems_info_list_map)
        return jsonify({'status_code':True,'problems_info_list':problems_info_list_map}),201

if __name__=='__main__':
    MySQLConnection('C:\\Users\\33007\\Desktop\\刷题网站\\多人在线刷题记录提交网站\\mysql_config.yml').get_connection()
    app.run(debug=True)