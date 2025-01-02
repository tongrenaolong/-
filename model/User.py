import hashlib
from flask import jsonify
from utils.logger import Logger
from model.database import db
# 用户表
class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False, default='bite')
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # relationships
    # problems = db.relationship('Problems', backref='user', lazy=True)
    # 使用 lazy 避免循环引用
    # user_problem_status = db.relationship('UserProblemStatus', backref='user', lazy=True)
    # user_subscriptions = db.relationship('UserSubscriptions', backref='user', lazy=True)
    problems = db.relationship('Problems', back_populates='user', lazy=True)
    user_problem_status = db.relationship('UserProblemStatus', back_populates='user', lazy=True)
    user_subscriptions = db.relationship('UserSubscriptions', back_populates='user', lazy=True)

    def __repr__(self):
        return f'<User {self.user_id},{self.account},{self.username},{self.password},{self.created_at}>'