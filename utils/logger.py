import logging
import threading

class Logger:
    _instance = None  # 存储单例实例
    _lock = threading.Lock()  # 用于线程安全的锁

    def __new__(cls, *args, **kwargs):
        with cls._lock:  # 确保线程安全
            if cls._instance is None:  # 如果实例为空，创建实例
                cls._instance = super().__new__(cls, *args, **kwargs)
                cls._instance._initialize_logger()  # 初始化日志记录器
        return cls._instance

    def _initialize_logger(self):
        """初始化日志记录器"""
        # 创建自定义日志格式
        log_format = '%(asctime)s [%(levelname)s] - %(module)s: %(funcName)s (line: %(lineno)d) - %(message)s'

        # 设置日志记录器
        self.logger = logging.getLogger('my_logger')
        self.logger.setLevel(logging.DEBUG)  # 设置日志记录器的最低级别

        # 创建日志处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)  # 设置控制台输出的日志级别

        # 设置日志格式
        formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(formatter)

        # 将处理器添加到日志记录器
        self.logger.addHandler(console_handler)

    def get_logger(self):
        """返回日志记录器实例"""
        return self.logger


# 示例使用
# def test_logging():
#     logger = Logger().get_logger()  # 获取单例日志记录器实例
#     logger.debug("This is a debug message")
#     logger.info("This is an info message")
#     logger.warning("This is a warning message")
#     logger.error("This is an error message")
#     logger.critical("This is a critical message")
#
# if __name__ == '__main__':
#     test_logging()
