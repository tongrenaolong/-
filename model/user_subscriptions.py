from utils.logger import Logger
from model.database import db

# 订阅表
class UserSubscriptions(db.Model):
    __tablename__ = 'user_subscriptions'

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    set_id = db.Column(db.Integer, db.ForeignKey('problem_sets.set_id'), primary_key=True)
    authority = db.Column(db.Boolean, default=False)

    # relationships
    user = db.relationship('User', back_populates='user_subscriptions', lazy=True)
    problem_set = db.relationship('ProblemSets', back_populates='user_subscriptions', lazy=True)

    def __repr__(self):
        return f'<UserSubscription {self.user_id},{self.set_id},{self.authority}>'