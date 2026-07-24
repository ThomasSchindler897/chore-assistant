from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Chore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    priority = db.Column(db.Integer, default=1)  # 1-5
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Chore {self.name}>'