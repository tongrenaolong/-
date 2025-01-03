import base64
import hashlib

from flask import Flask, render_template, request, make_response, redirect, url_for, jsonify, session
from sqlalchemy import func

from model.User import User
from utils.logger import Logger
from model.problem_sets import ProblemSets
from model.user_subscriptions import UserSubscriptions
from model.problems import Problems
from model.user_problem_status import UserProblemStatus
import secrets
from datetime import timedelta
from utils.web import get_user_info
from model.database import Database,db

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # 将生成的随机密钥用于 Flask 配置
app.permanent_session_lifetime = timedelta(days=7)  # 设置 Session 7 天后过期
Database(app)# 这里只进行配置，使用的时候需要引入 database 中的 db 然后使用

def verify_login():
    # print('user_info: ',get_user_info())
    # user_info = request.cookies.get('user_info')
    user_info = get_user_info()
    Logger().get_logger().info(f'user_info: {user_info}')
    if user_info is None:
        return False
    password = hashlib.md5(user_info['password'].encode()).hexdigest()
    user = db.session.query(User).filter(User.account == user_info['account'], User.password == password).first()
    if user is not None:
        return True
    else:
        return False

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
    password = hashlib.md5(user_info['password'].encode()).hexdigest()
    user = db.session.query(User).filter(User.account == user_info['account'], User.password == password).first()
    Logger().get_logger().info(f'result: {user}')

    if user:
        print("Login successful!")
        session.permanent = True
        user_id = user.user_id
        Logger().get_logger().info(user.user_id)
        user_info['user_id'] = user_id
        session['user_info'] = user_info
        Logger().get_logger().info("session[user_info]: ", session['user_info'])
        return jsonify({'status_code': True, 'message': '登录成功', 'account': user_info['account']})
    else:
        print("Invalid username or password.")
        return jsonify({'status_code': False, 'message': '登录失败', 'account': user_info['account']})


@app.route('/register',methods=['POST'])
def register():
    data = request.get_json()
    Logger().get_logger().info(data)
    try:
        password = hashlib.md5(data['password'].encode()).hexdigest()
        db.session.add(User(username=data['username'],account=data['account'], password=password))
        db.session.commit()
        Logger().get_logger().info(f"{data['account']} 插入成功")
        return jsonify({'status_code': True, 'message': '注册成功', 'account': data['account']})
    except Exception as e:
        db.session.rollback()
        Logger().get_logger().info(f"{data['account']} 插入失败; {e}")
        return jsonify({'status_code': False, 'message': '注册失败', 'account': data['account']})

@app.route('/main', methods=['GET'])
def main():
    return render_template('main.html')  # 返回 main.html 页面

@app.route('/create_problems', methods=['POST'])
def create_problems():
    user_info = get_user_info()
    user_id = user_info['user_id']
    data = request.get_json()
    set_id = data['set_id']
    try:
        for problem in data['questions']:
            new_problem = Problems(problem_name=problem['name'],link=problem['link'],difficulty=problem['difficulty'],user_id=user_id,set_id=data['set_id'])
            db.session.add(new_problem)
            db.session.flush()
            new_problem_id = new_problem.problem_id
            # 给每一个订阅题单的用户添加 problem-user
            all_users = db.session.query(UserSubscriptions.user_id).filter(UserSubscriptions.set_id == set_id).all()
            for user in all_users:
                Logger().get_logger().info(f"user: {user}")
                new_user_problem_status = UserProblemStatus(user_id=user[0],problem_id=new_problem_id)
                db.session.add(new_user_problem_status)
        db.session.commit()
        return jsonify({'status_code':True,'message':'新增题目成功'}),201
    except Exception as e:
        db.session.rollback()
        Logger().get_logger().error(f'新增题目失败; {e}')
        return jsonify({'status_code':False,'message':'新增题目失败'}),201

@app.route('/create_set', methods=['POST'])
def create_set():
    user_info = get_user_info()
    data = request.get_json()
    # {'title': 'asdf', 'questions': [{'name': 'adf', 'link': 'asdf', 'difficulty': 'easy'}]}
    # print(user_info)
    Logger().get_logger().info(user_info)
    try:
        # 新建题集没有任何要求
        new_set = ProblemSets(set_name=data['title'],description=data['description'])
        db.session.add(new_set)
        db.session.flush()
        new_set_id = new_set.set_id
        Logger().get_logger().info(f'new_set_id: {new_set_id}')
        db.session.add(UserSubscriptions(user_id=user_info['user_id'],set_id=new_set_id,authority=True))
        # 创建题目
        # 一个题单中一个题目只能出现一次
        for problem in data['questions']:
            result = db.session.query(Problems).filter(Problems.link == problem['link'],Problems.set_id == new_set_id).first()
            if result is None:
                Logger().get_logger().info(f'problem: {problem}')
                problem_name = problem['problem_name']
                new_problem = Problems(problem_name=problem['problem_name'],link = problem['link'],set_id= new_set_id,difficulty=problem['difficulty'],user_id=user_info['user_id'])
                db.session.add(new_problem)
                db.session.flush()
                problem_id = new_problem.problem_id
                new_user_problem_status = UserProblemStatus(user_id=user_info['user_id'],problem_id=problem_id)
                db.session.add(new_user_problem_status)
        db.session.commit()
        return jsonify({'status_code': True, 'message': '注册题单成功'}), 200
    except Exception as e:
        db.session.rollback()
        Logger().get_logger().error(f'{user_info}:{data} 创建题单失败; {e}')
        return jsonify({'status_code':False,'message':'创建题单失败'}),201

@app.route('/get_sets', methods=['GET'])
def get_sets():
    user_info = get_user_info()
    # 通过 user_info 得到他加入的所有 problem_set
    # 返回 problem_sets
    # 查询订阅表，获取 set_id
    subscribed_sets = (
        db.session.query(ProblemSets)
        .join(UserSubscriptions, ProblemSets.set_id == UserSubscriptions.set_id)
        .filter(UserSubscriptions.user_id == user_info['user_id'])
        .all()
    )
    Logger().get_logger().info(f'subscribed_sets: {subscribed_sets}')
    sets = []
    for set in subscribed_sets:
        tem = {
            'set_id': set.set_id,
            'set_name': set.set_name,
            'created_at': set.created_at,
            'description': set.description,
        }
        sets.append(tem)
        Logger().get_logger().info(f'tem: {tem}')
    Logger().get_logger().info(f'sets: {sets}')
    return jsonify({'status_code':True,'sets':sets}),201

@app.route('/get_set_problems',methods=['GET'])
def get_set_problems():
    user_info = get_user_info()
    user_id = user_info['user_id']
    set_id = int(request.args.get('set_id', 0))
    try:
        user_subscription = db.session.query(UserSubscriptions).filter(UserSubscriptions.user_id == user_id,UserSubscriptions.set_id == set_id).first()
        if user_subscription is None:
            return jsonify({'status_code':False,'message':'题单不存在'}),201
        else:
            problems_info_list = []
            authority = user_subscription.authority
            problem_list = db.session.query(Problems).filter(Problems.set_id == set_id).all()
            Logger().get_logger().info(f'len(problem_list): {len(problem_list)}')
            for problem in problem_list:
                tem = dict()
                tem['problem_name'] = problem.problem_name
                tem['link'] = problem.link
                tem['difficulty'] = problem.difficulty
                problem_id = problem.problem_id
                tem['problem_id'] = problem_id
                Logger().get_logger().info(f'problem_name: {problem.problem_name},problem_id: {problem_id}')
                all_count = (
                    db.session.query(func.count(UserProblemStatus.user_id))
                    .filter(UserProblemStatus.problem_id == problem_id)
                    .scalar()
                )
                completed_count = (
                    db.session.query(func.count(UserProblemStatus.user_id))
                    .filter(UserProblemStatus.problem_id == problem_id,UserProblemStatus.status == 'completed')
                    .scalar()
                )
                myself_status = (
                    db.session.query(UserProblemStatus)
                    .filter(UserProblemStatus.problem_id == problem_id,UserProblemStatus.user_id == user_id)
                    .first()
                )
                Logger().get_logger().info(myself_status)
                tem['all'] = all_count
                tem['completed'] = completed_count
                tem['status'] = myself_status.status
                problems_info_list.append(tem)
            Logger().get_logger().info(f'problems_info_list: {problems_info_list}')
            return jsonify({'status_code':True,'authority':authority,'problems_info_list':problems_info_list}),201
    except Exception as e:
        Logger().get_logger().error(e)
        return jsonify({'status_code':False,'message':'查询失败,请稍后重试'}),201

@app.route('/delete_set_id',methods=['GET'])
def delete_set_id():
    user_info = get_user_info()
    user_id = user_info['user_id']
    set_id = request.args.get('set_id')

    # 判断当前用户是否加入题单
    user_subscription = db.session.query(UserSubscriptions).filter(UserSubscriptions.user_id == user_id,UserSubscriptions.set_id == set_id).first()
    if user_subscription is not None:
        # 删除当前用户对应题单中每个题目的状态
        # 子查询筛选出符合条件的 user_id 和 problem_id
        subquery = (
            db.session.query(UserProblemStatus.user_id, UserProblemStatus.problem_id)
            .join(Problems, UserProblemStatus.problem_id == Problems.problem_id)
            .filter(Problems.set_id == set_id,UserProblemStatus.user_id == user_id)
            .subquery()
        )

        # 删除符合条件的记录
        db.session.query(UserProblemStatus).filter(
            UserProblemStatus.user_id.in_(db.session.query(subquery.c.user_id)),
            UserProblemStatus.problem_id.in_(db.session.query(subquery.c.problem_id)),
        ).delete(synchronize_session=False)
        # 将 user 对应的题单删除
        db.session.query(UserSubscriptions).filter(UserSubscriptions.set_id == set_id,UserSubscriptions.user_id == user_id).delete()
        Logger().get_logger().info(f'authority: {user_subscription.authority}')
        if user_subscription.authority:
            db.session.query(Problems).filter(Problems.set_id == set_id).delete(synchronize_session=False)
            db.session.query(ProblemSets).filter(ProblemSets.set_id == set_id).delete(synchronize_session=False)
            Logger().get_logger().info(f"{user_info['account']} 是这道题的创建者")
        db.session.commit()
        return jsonify({'status_code':True,'message':'删除成功'}),201
    else:
        Logger().get_logger().info(f"account: {user_info['account']},set_id: {set_id} 不存在")
        return jsonify({'status_code':True,'message':'用户并未加入此提单'}),201

@app.route('/upload_solution',methods=['POST'])
def upload_solution():
    user_info = get_user_info()
    user_id = user_info['user_id']
    set_id = request.form.get('set_id')
    problem_id = request.form.get('problem_id')
    Logger().get_logger().info(f'problem_id: {problem_id}')
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
        (
            db.session.query(UserProblemStatus)
            .filter(UserProblemStatus.problem_id == problem_id,UserProblemStatus.user_id == user_id)
            .update({"status": status, "description": input_text,'image':image_data}, synchronize_session=False)
        )
        db.session.commit()
        return jsonify({'status_code':True,'message':'打卡成功'}),201
    except Exception as e:
        db.session.rollback()
        return jsonify({'status_code':False,'message':'打卡失败'}),201


@app.route('/search_problem_sets',methods=['GET'])
def search_problem_sets():
    user_info = get_user_info()
    user_id = user_info['user_id']
    set_name = str(request.args.get('set_name', ''))
    try:
        subquery = (
            db.session.query(ProblemSets)
            .filter(ProblemSets.set_name == set_name)
            .all()
        )
        set_id_list = []
        for set_info in subquery:
            ret = db.session.query(UserSubscriptions).filter(UserSubscriptions.set_id == set_info.set_id,UserSubscriptions.user_id == user_id).first()
            if ret is None:
                set_id_list.append(set_info.set_id)
        set_data_list = []
        for set_id in set_id_list:
            set_data = dict()
            ret = db.session.query(ProblemSets).filter(ProblemSets.set_id == set_id).first()
            if ret is not None:
                set_data['set_id'] = ret.set_id
                set_data['set_name'] = ret.set_name
                set_data['created_at'] = ret.created_at
                set_data['description'] = ret.description
            total_problems = (
                db.session.query(func.count(Problems.problem_id))
                .filter(Problems.set_id == set_id)
                .scalar()
            )
            set_data['total_problems'] = total_problems
            members_count = (
                db.session.query(func.count(UserSubscriptions.user_id))
                .filter(UserSubscriptions.set_id == set_id)
                .scalar()
            )
            set_data['members_count'] = members_count
            # 使用联合查询根据 set_id 查找对应的 account
            result = db.session.query(User.account).join(
                UserSubscriptions, User.user_id == UserSubscriptions.user_id
            ).filter(
                UserSubscriptions.set_id == set_id  # 根据 set_id 过滤
            ).first()
            if result is not None:
                set_data['account'] = result.account

            set_data_list.append(set_data)
            Logger().get_logger().info(f'set_data: {set_data}')
        return jsonify({'status_code': True,
                        'message': '查找所有问题集成功',
                        'set_data_list': set_data_list}), 201
    except Exception as e:
        return jsonify({'status_code': False,'message':'查找输出'}),201

@app.route('/join_problem_set',methods=['POST'])
def join_problem_set():
    user_info = get_user_info()
    user_id = user_info['user_id']
    set_id_list = request.json.get('set_id_list')
    try:
        for set_id in set_id_list:
            new_user_subscription = UserSubscriptions(user_id=user_id, set_id=set_id,authority=False)
            db.session.add(new_user_subscription)
            problem_ids = db.session.query(Problems.problem_id).filter(Problems.set_id == set_id).all()

            for problem_id in problem_ids:
                Logger().get_logger().info(f'problem_id: {problem_id}')
                new_problem_status = UserProblemStatus(user_id=user_id, problem_id=problem_id[0])
                db.session.add(new_problem_status)
        db.session.commit()
        return jsonify({'status_code': True, 'message': '加入成功'}), 201
    except Exception as e:
        db.session.rollback()
        Logger().get_logger().error(f'加入题单失败; {e}')
        return jsonify({'status_code': False,'message':'加入失败'}),201

@app.route('/main/delete_problem',methods=['GET'])
def delete_problem():
    pass

@app.route('/get_account_info',methods=['GET'])
def get_account_info():
    user_info = get_user_info()
    print('user_info: ', user_info)
    return jsonify({'status_code':True,'message':'获取用户信息成功','user_id': user_info}),201

if __name__=='__main__':
    app.run(host='0.0.0.0',port=8080)