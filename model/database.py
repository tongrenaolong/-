import yaml
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from urllib.parse import quote_plus

# 创建 SQLAlchemy 实例
db = SQLAlchemy()


class Database:
    def __init__(self, app=None):
        """
        初始化数据库连接类
        如果传入 app，则立即将其与 Flask 应用绑定
        """
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask,config_file='./mysql_config.yml'):
        """
        初始化 Flask 应用与数据库
        """
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)  # 读取 YAML 文件
        mysql = config['mysql']
        host = mysql['host']
        username = mysql['username']
        password = mysql['password']
        database = mysql['database']
        encoded_password = quote_plus(password)
        app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{encoded_password}@{host}/{database}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_POOL_SIZE'] = 10  # 连接池大小
        app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600  # 连接最大生命周期

        # 将 SQLAlchemy 与 Flask 应用绑定
        db.init_app(app)