from flask import Flask, render_template, request, redirect
from models import db, Chore
from datetime import datetime

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chores.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with app
db.init_app(app)

@app.route('/')
def home():
    all_chores = Chore.query.all()
    todays_chores = [chore for chore in all_chores if chore.is_due_today() and not chore.completed]
    completed_today = [chore for chore in all_chores if chore.is_due_today() and chore.completed]
    overdue_chores = [chore for chore in all_chores if chore.is_overdue()]
    
    today_date = datetime.now().strftime('%A, %B %d, %Y')
    
    return render_template('home.html', 
                         chores=todays_chores, 
                         completed_chores=completed_today,
                         overdue_chores=overdue_chores,
                         today_date=today_date)

@app.route('/toggle/<int:chore_id>', methods=['POST'])
def toggle_chore(chore_id):
    from flask import redirect
    chore = Chore.query.get_or_404(chore_id)
    chore.completed = not chore.completed
    
    if chore.completed:
        chore.last_completed = datetime.now()
    
    db.session.commit()
    return redirect('/')

@app.route('/chores')
def chores():
    all_chores = Chore.query.all()
    return render_template('chores.html', chores=all_chores)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/edit/<int:chore_id>', methods=['GET', 'POST'])
def edit_chore(chore_id):
    from flask import request, redirect
    chore = Chore.query.get_or_404(chore_id)
    
    if request.method == 'POST':
        chore.name = request.form['name']
        chore.description = request.form['description']
        chore.priority = int(request.form['priority'])
        chore.completed = request.form.get('completed') == 'on'
        
        db.session.commit()
        return redirect('/chores')
    
    return render_template('edit_chore.html', chore=chore)

@app.route('/delete/<int:chore_id>', methods=['POST'])
def delete_chore(chore_id):
    from flask import redirect
    chore = Chore.query.get_or_404(chore_id)
    db.session.delete(chore)
    db.session.commit()
    return redirect('/chores')

if __name__ == '__main__':
    app.run(debug=True)