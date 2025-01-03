# 使用官方 Python 镜像
FROM python:latest
# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 到容器中
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码到容器中
COPY . .

# 暴露应用所使用的端口
EXPOSE 8080

# 启动 Flask 应用
CMD ["python3", "main.py"]
