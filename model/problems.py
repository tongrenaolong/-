from utils.logger import Logger
from model.database import db

# 题目表
class Problems(db.Model):
    __tablename__ = 'problems'

    problem_id = db.Column(db.Integer, primary_key=True)
    problem_name = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(255), nullable=False)
    upload_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    difficulty = db.Column(db.Enum('easy', 'medium', 'hard'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    set_id = db.Column(db.Integer, db.ForeignKey('problem_sets.set_id'), nullable=False)

    # relationships
    user = db.relationship('User', back_populates='problems', lazy=True)
    problem_statuses = db.relationship('UserProblemStatus', back_populates='problems', lazy=True)
    problem_sets = db.relationship('ProblemSets', back_populates='problems', lazy=True)

    def __repr__(self):
        return f'<Problem {self.problem_id},{self.problem_name},{self.link},{self.upload_time},{self.difficulty},{self.user_id}>'