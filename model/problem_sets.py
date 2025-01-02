from model.database import db

# 题单表
class ProblemSets(db.Model):
    __tablename__ = 'problem_sets'

    set_id = db.Column(db.Integer, primary_key=True)
    set_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    description = db.Column(db.Text)

    # relationships
    # user_subscriptions = db.relationship('UserSubscriptions', backref='problem_set', lazy=True)
    # problem_set_problems = db.relationship('ProblemSetProblems', backref='problem_set', lazy=True)
    user_subscriptions = db.relationship('UserSubscriptions', back_populates='problem_set', lazy=True)
    problems = db.relationship('Problems', back_populates='problem_sets', lazy=True)

    def __repr__(self):
        return f'<ProblemSet {self.set_id},{self.set_name},{self.created_at},{self.description}>'