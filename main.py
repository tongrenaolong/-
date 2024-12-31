import base64
import datetime
import json

from flask import Flask, render_template, request, make_response, redirect, url_for, jsonify, session
from model.User import User
from utils.logger import Logger
from utils.mysql_config import MySQLConnection

from model.problem_sets import ProblemSets
from model.user_subscriptions import UserSubscriptions
from model.problem_set_problems import ProblemSetProblems
from model.problems import Problems
from model.user_problem_status import UserProblemStatus
import secrets
from datetime import timedelta
from utils.web import get_user_info

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # 将生成的随机密钥用于 Flask 配置
app.permanent_session_lifetime = timedelta(days=7)  # 设置 Session 7 天后过期

def verify_login():
    # print('user_info: ',get_user_info())
    # user_info = request.cookies.get('user_info')
    user_info = get_user_info()
    if user_info is None:
        return False
    resp = User().login(user_info)
    return resp.get_json().get('status_code')

@app.before_request
def before_request():
    path = request.path
    Logger().get_logger().info(path)
    # 排除公开访问的路径
    if path in ['/register', '/','/login']:
        return

    # 其他路径检查登录状态
    if not verify_login():
        return render_template('home.html',data={"status_code":False,"message":"用户未登录"})

@app.route('/',methods=['GET','POST'])
def index():
    return render_template('home.html')

@app.route('/login',methods=['POST'])
def login():
    user_info = request.get_json()
    Logger().get_logger().info(user_info)
    resp = make_response(User().login(user_info)) # account,password
    # 设置一个 Cookie（例如，保存用户名）
    # resp.set_cookie('user_info', json.dumps(user_info), expires=datetime.datetime.now())
    # print("user_info: ",user_info)
    session.permanent = True
    session['user_info'] = user_info
    print("session[user_info]: ",session['user_info'])
    return resp

@app.route('/register',methods=['POST'])
def register():
    data = request.get_json()
    Logger().get_logger().info(data)
    try:
        User().register(data)
        Logger().get_logger().info(f"{data['account']} 插入成功")
        return jsonify({'status_code': True, 'message': '注册成功', 'account': data['account']})
    except Exception as e:
        Logger().get_logger().error(e)
        Logger().get_logger().info(f"{data['account']} 插入失败")
        return jsonify({'status_code': False, 'message': '注册失败', 'account': data['account']})

@app.route('/main', methods=['GET'])
def main():
    return render_template('main.html')  # 返回 main.html 页面

@app.route('/create_problems', methods=['POST'])
def create_problems():
    # user_info_str = request.cookies.get('user_info')
    # user_info = json.loads(user_info_str)
    # user_id = User().get_user_id(user_info['account'])
    user_info = get_user_info()
    Logger().get_logger().info(user_info)
    user_id = User().get_user_id(user_info['account'])
    data = request.get_json()
    try:
        MySQLConnection().get_connection().begin()
        if UserSubscriptions().check_exist_authority(data['set_id'],user_id,True):
            problems_id_list = Problems().create_problems(data['questions'],user_id)
            ProblemSetProblems().insert_problems(data['set_id'],problems_id_list)
            UserProblemStatus().create(user_id,problems_id_list)
            MySQLConnection().get_connection().commit()
            return jsonify({'status_code':True,'message':'新增题目成功'}),201
        else:
            MySQLConnection().get_connection().commit()
            return jsonify({'status_code':False,'message':'你无权创建题目'}),201
    except Exception as e:
        Logger().get_logger().error(e)
        Logger().get_logger().error(f'{user_id}:{data} 创建题目失败')
        MySQLConnection().get_connection().rollback()
        return jsonify({'status_code':False,'message':'创建题目失败'}),201


@app.route('/create_set', methods=['POST'])
def create_set():
    user_info = get_user_info()
    data = request.get_json()
    # {'title': 'asdf', 'questions': [{'name': 'adf', 'link': 'asdf', 'difficulty': 'easy'}]}
    # print(user_info)
    Logger().get_logger().info(user_info)
    try:
        MySQLConnection().get_connection().begin()
        check_exist = ProblemSets().check_set_exist(user_info, data)
        if check_exist:
            Logger().get_logger().info(f"{data['title']} already exists")
            MySQLConnection().get_connection().commit()
            return jsonify({'status_code': False,'message':'题单已经存在'}),200
        else:
            Logger().get_logger().info(f"{data['title']} 不存在")
            user_id = User().get_user_id(user_info['account'])
            ProblemSets().create_problem_set(data['title'], data['description'])
            # set_id = ProblemSets().get_current_set_id()
            set_id = ProblemSets().get_last_set_id_test()
            Logger().get_logger().info(f'set_id: {set_id}')
            UserSubscriptions().check_exist(set_id, user_id)
            UserSubscriptions().create(set_id, user_id, True) # 外键
            problems_id_list = Problems().create_problems(data['questions'], user_id)
            ProblemSetProblems().insert_problems(set_id,problems_id_list)
            UserProblemStatus().create(user_id, problems_id_list)
            MySQLConnection().get_connection().commit()
            return jsonify({'status_code': True, 'message': '注册题单成功'}), 200
    except Exception as e:
        Logger().get_logger().error(e)
        Logger().get_logger().error(f'{user_info}:{data} 创建题单失败')
        MySQLConnection().get_connection().rollback()
        return jsonify({'status_code':False,'message':'创建题单失败'}),201

@app.route('/get_sets', methods=['GET'])
def get_sets():
    user_info = get_user_info()
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
    # 将最后返回的元素转成 list
    return jsonify({'status_code':True,'sets':ret_list}),201

@app.route('/get_set_problems',methods=['GET'])
def get_set_problems():
    user_info = get_user_info()
    user_id = User().get_user_id(user_info['account'])
    # 由于 set_id 是唯一的，只需要通过 set_id 查找就可以了
    set_id = int(request.args.get('set_id', 0))
    print("set_id: ",set_id)
    result = ProblemSets().check_problem_sets_exist(set_id)
    if result is False:
        return jsonify({'status_code':False,'message':'题单不存在'}),201
    else:
        authority = UserSubscriptions().check_exist_authority(set_id, user_id, True)
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
        return jsonify({'status_code':True,'authority':authority,'problems_info_list':problems_info_list_map}),201

@app.route('/delete_set_id',methods=['GET'])
def delete_set_id():
    user_info = get_user_info()
    user_id = User().get_user_id(user_info['account'])
    # 由于 set_id 是唯一的，只需要通过 set_id 查找就可以了
    set_id = int(request.args.get('set_id', 0))
    try:
        MySQLConnection().get_connection().begin()
        if UserSubscriptions().check_exist(set_id,user_id):
            problems_id_list = ProblemSetProblems().get_problems_list(set_id)
            if UserSubscriptions().check_exist_authority(set_id,user_id,True):
                ProblemSetProblems().delete_set_id(set_id)
                ProblemSets().delete_set_id(set_id)
                Problems().delete_problems_id_list(problems_id_list)
                UserProblemStatus().delete_problems_id_list(problems_id_list)
                UserSubscriptions().delete_set_id(set_id)
                Logger().get_logger().info('删除成功')
            else:
                for problem_id in problems_id_list:
                    UserProblemStatus().delete_problem_id(user_id,problem_id)
                    UserSubscriptions().delete_info(user_id,set_id)
            MySQLConnection().get_connection().commit()
            return jsonify({'status_code':True,'message':'题单删除成功'}),201
        else:
            MySQLConnection().get_connection().commit()
            return jsonify({'status_code':False,'message':'无权删除'}),201
    except Exception as e:
        Logger().get_logger().error(f'{set_id}:{user_id} 删除题单失败')
        MySQLConnection().get_connection().rollback()
        return jsonify({'status_code':False,'message':'删除题单失败'}),201

@app.route('/upload_solution',methods=['POST'])
def upload_solution():
    user_info = get_user_info()
    user_id = User().get_user_id(user_info['account'])

    set_id = request.form.get('set_id')
    problem_id = request.form.get('problem_id')
    status = request.form.get('status') # 题目状态，未开始/完成
    input_text = request.form.get('input_text')
    # 获取 Base64 编码的图片数据
    base64_image = request.form.get('image_data')
    image_data = None
    if base64_image:
        # 可能会有 "data:image/png;base64," 的前缀，去除它
        if base64_image.startswith('data:image'):
            base64_image = base64_image.split(',')[1]
            # 解码 Base64 数据为二进制
            image_data = base64.b64decode(base64_image)
    try:
        MySQLConnection().get_connection().begin()
        if ProblemSetProblems().check_exist(set_id,problem_id):
            UserProblemStatus().refreshStatus(user_id, problem_id,status, input_text, image_data)
            MySQLConnection().get_connection().commit()
            return jsonify({'status_code':True,'message':'打卡成功'}),201
        else:
            MySQLConnection().get_connection().commit()
            return jsonify({'status_code':False,'message':'题单已删除'}),201
    except Exception as e:
        MySQLConnection().get_connection().rollback()
        return jsonify({'status_code':False,'message':'打卡失败'}),201


@app.route('/search_problem_sets',methods=['GET'])
def search_problem_sets():
    user_info = get_user_info()
    user_id = User().get_user_id(user_info['account'])

    set_name = str(request.args.get('set_name', ''))
    set_id_list = ProblemSets().get_set_id_list(set_name)
    user_id_list = UserSubscriptions().get_user_id_list(set_id_list) # user_id

    problem_sets_list = ProblemSets().get_problem_sets_list(set_id_list) # set_id,set_name,created_at,description
    Logger().get_logger().info(f'len(set_id_list) = {len(set_id_list)}, len(user_id_list) = {len(user_id_list)}, len(problem_sets_list)={len(problem_sets_list)}')
    for i in range(len(problem_sets_list)):
        if UserSubscriptions().check_exist(set_id_list[i],user_id): # BUG
            set_id_list.remove(set_id_list[i])
            user_id_list.remove(user_id_list[i])
            problem_sets_list.remove(problem_sets_list[i])
            break
    account_list = []
    for user_id in user_id_list:
        account_list.append(User().get_account(user_id))
    for i in range(len(user_id_list)):
        problem_sets_list[i].append(user_id_list[i])
    count_problem_set_list = []
    for set_id in set_id_list:
        count_problem_set_list.append(ProblemSetProblems().count_problem_set(set_id))
    count_problem_set_member_list = []
    for set_id in set_id_list:
        count_problem_set_member_list.append(UserSubscriptions().count_member(set_id))
    print(problem_sets_list)
    set_data_list = []
    for i in range(len(problem_sets_list)):
        set_data = dict()
        set_data['set_id'] = set_id_list[i]
        set_data['set_name'] = set_name
        set_data['account'] = account_list[i]
        set_data['created_at'] = problem_sets_list[i][2]
        set_data['description'] = problem_sets_list[i][3]
        set_data['total_problems'] = count_problem_set_list[i]
        set_data['members_count'] = count_problem_set_member_list[i]
        set_data_list.append(set_data)
    print('set_data_list: ',set_data_list)
    return jsonify({'status_code': True,
                    'message': '查找所有问题集成功',
                    'set_data_list': set_data_list}), 201

@app.route('/join_problem_set',methods=['POST'])
def join_problem_set():
    user_info = get_user_info()
    user_id = User().get_user_id(user_info['account'])

    set_id_list = request.json.get('set_id_list')
    print('set_id_list: ', set_id_list)

    try:
        MySQLConnection().get_connection().begin()
        for set_id in set_id_list:
            UserSubscriptions().create(set_id,user_id,False)
            problems_id_list = ProblemSetProblems().get_problems_list(set_id) # 获取一个题单中的所有题目
            UserProblemStatus().create(user_id, problems_id_list)
        MySQLConnection().get_connection().commit()
        return jsonify({'status_code': True, 'message': '加入成功'}), 201
    except Exception as e:
        MySQLConnection().get_connection().rollback()
        return jsonify({'status_code': False,'message':'插入失败'}),201

@app.route('/main/delete_problem',methods=['GET'])
def delete_problem():
    pass

@app.route('/get_account_info',methods=['GET'])
def get_account_info():
    user_info = get_user_info()
    print('user_info: ', user_info)
    return jsonify({'status_code':True,'message':'获取用户信息成功','user_id': user_info}),201

if __name__=='__main__':
    MySQLConnection('./mysql_config.yml').get_connection()
    app.run(debug=True)