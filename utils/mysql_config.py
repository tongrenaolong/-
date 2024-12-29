import pymysql
import yaml
import threading
from utils.logger import Logger


class MySQLConnection:
    _instance = None  # 存储单例实例
    _lock = threading.Lock()  # 用于线程安全的锁

    def __new__(cls, config_file=None):
        # Logger().get_logger().info(f"{config_file}")
        with cls._lock:  # 确保线程安全
            if cls._instance is None:  # 如果实例为空，创建实例
                cls._instance = super(MySQLConnection, cls).__new__(cls)
                cls._instance._connect(config_file)  # 初始化数据库连接
        return cls._instance

    def _connect(self, config_file='../mysql_config.yml'):
        """加载配置文件并连接数据库"""
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)  # 读取 YAML 文件
        mysql = config['mysql']
        self.host = mysql['host']
        self.username = mysql['username']
        self.password = mysql['password']
        self.database = mysql['database']

        # 创建数据库连接
        self.connection = pymysql.connect(
            host=self.host,
            user=self.username,
            password=self.password,
            database=self.database,
            charset='utf8mb4'
        )
        self.cursor = self.connection.cursor()

    def get_connection(self):
        """返回数据库连接"""
        return self.connection

    def get_cursor(self):
        """返回数据库游标"""
        return self.cursor

    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

# # 示例使用
# def test_connection():
#     # 获取 MySQL 单例连接，传入配置文件路径
#     db_connection = MySQLConnection("../mysql_config.yml")
#
#     # 使用连接执行查询
#     cursor = db_connection.get_cursor()
#     cursor.execute("SELECT VERSION()")
#     version = cursor.fetchone()
#     print("MySQL version:", version)
#
#     # 关闭连接
#     db_connection.close()