from utils.logger import Logger
from model.database import db

# 刷题状态表
class UserProblemStatus(db.Model):
    __tablename__ = 'user_problem_status'

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.problem_id'), primary_key=True)
    status = db.Column(db.Enum('not_started', 'completed'), default='not_started')
    time_spent = db.Column(db.Integer, default=0)  # time in seconds
    description = db.Column(db.Text, default=None)
    image = db.Column(db.LargeBinary, default=None)

    # relationships
    user = db.relationship('User', back_populates='user_problem_status', lazy=True)
    problems = db.relationship('Problems', back_populates='problem_statuses', lazy=True)

    def __repr__(self):
        return f'<UserProblemStatus {self.user_id},{self.problem_id},{self.status},{self.time_spent},{self.description}>'