from flask import session
from utils.logger import Logger

def get_user_info():
    user_info = None
    if 'user_info' in session:
        Logger().get_logger().info(session['user_info'])
        user_info = session['user_info']
    return user_info
