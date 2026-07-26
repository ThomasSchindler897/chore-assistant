from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Chore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    priority = db.Column(db.Integer, default=1)  # 1-5
    completed = db.Column(db.Boolean, default=False)
    
    # New frequency fields
    frequency = db.Column(db.String(20), default='daily')  # daily, weekly, monthly, once
    frequency_details = db.Column(db.String(200))  # e.g., "Monday,Wednesday" or "2,15" for dates

    def __repr__(self):
        return f'<Chore {self.name}>'