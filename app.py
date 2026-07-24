from flask import Flask, render_template
from models import db, Chore

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chores.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with app
db.init_app(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/chores')
def chores():
    all_chores = Chore.query.all()
    return render_template('chores.html', chores=all_chores)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)