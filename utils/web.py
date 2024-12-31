from flask import session
from utils.logger import Logger

def get_user_info():
    user_info = None
    try:
        Logger().get_logger().info(session['user_info'])
        user_info = session['user_info']
    except Exception as e:
        print('error: ',e)
    return user_info
