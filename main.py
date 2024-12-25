import datetime

from flask import Flask, render_template, request, make_response, redirect, url_for, jsonify
from utils.User import User
from utils.logger import Logger
from utils.mysql_config import MySQLConnection
from utils.quiz import Quiz

app = Flask(__name__)

def verify_login():
    user_info = request.cookies.get('user_info')
    Logger().get_logger().info(user_info)
    user = User()
    resp = user.login(user_info)
    return resp['status_code']

@app.before_request
def before_request():
    path = request.path
    # 如果是从登录页面进行请求并且验证通过
    if path == '/login' and verify_login():
        return redirect(url_for('main'))
    # 排除注册接口
    if path == '/register':
        return
    # 检查是否已经登录（检查 Cookie 中的用户信息）
    if path != '/login' and not verify_login():
        # 如果没有登录，返回 401 未授权
        return jsonify({"status_code": 401, "message": "未登录"}), 401

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
    resp.set_cookie('user_info', user_info, expires=datetime.datetime.now() + datetime.timedelta(days=1))
    return resp

@app.route('/register',methods=['POST'])
def register():
    data = request.get_json()
    Logger().get_logger().info(data)
    user = User()
    return user.register(data)

@app.before_request
@app.route('/main', methods=['GET'])
def main():
    return render_template('main.html')  # 返回 main.html 页面

@app.before_request
@app.route('/create_quiz', methods=['POST'])
def create_quiz():
    data = request.get_json()
    user_info = data['user_info']
    # {'title': 'asdf', 'questions': [{'name': 'adf', 'link': 'asdf', 'difficulty': 'easy'}]}
    print(user_info)
    Quiz().create(user_info,data)
    return "hello"

if __name__=='__main__':
    MySQLConnection('C:\\Users\\33007\\Desktop\\刷题网站\\多人在线刷题记录提交网站\\mysql_config.yml').get_connection()
    app.run(debug=True)