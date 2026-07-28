from flask import Flask, render_template, request, redirect
from models import db, Chore, Completion
from datetime import datetime, date

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chores.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with app
db.init_app(app)

# Create tables on first run
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    all_chores = Chore.query.all()
    todays_chores = [chore for chore in all_chores if chore.is_due_today() and not chore.completed]
    completed_today = [chore for chore in all_chores if chore.completed]
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
    from datetime import date
    
    chore = Chore.query.get_or_404(chore_id)
    chore.completed = not chore.completed
    
    if chore.completed:
        chore.last_completed = datetime.now()
        # Only add completion if one doesn't already exist for today
        today = date.today()
        existing_today = Completion.query.filter(
            Completion.chore_id == chore.id,
            db.func.date(Completion.completed_at) == today
        ).first()
        
        if not existing_today:
            completion = Completion(chore_id=chore.id)
            db.session.add(completion)
    else:
        # If unchecking, remove today's completion entry
        today = date.today()
        completion_today = Completion.query.filter(
            Completion.chore_id == chore.id,
            db.func.date(Completion.completed_at) == today
        ).first()
        
        if completion_today:
            db.session.delete(completion_today)
    
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
    chore = Chore.query.get_or_404(chore_id)
    
    if request.method == 'POST':
        chore.name = request.form['name']
        chore.description = request.form['description']
        chore.priority = int(request.form['priority'])
        chore.frequency = request.form['frequency']
        chore.frequency_details = request.form.get('frequency_details') or None
        chore.completed = request.form.get('completed') == 'on'
        
        db.session.commit()
        return redirect('/chores')
    
    return render_template('edit_chore.html', chore=chore)

@app.route('/add', methods=['GET', 'POST'])
def add_chore():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description') or None
        priority = int(request.form['priority'])
        frequency = request.form['frequency']
        frequency_details = request.form.get('frequency_details') or None
        
        new_chore = Chore(
            name=name,
            description=description,
            priority=priority,
            frequency=frequency,
            frequency_details=frequency_details
        )
        
        db.session.add(new_chore)
        db.session.commit()
        return redirect('/chores')
    
    return render_template('add_chore.html')

@app.route('/stats')
def stats():
    all_chores = Chore.query.all()
    return render_template('stats.html', chores=all_chores)

@app.route('/delete/<int:chore_id>', methods=['POST'])
def delete_chore(chore_id):
    from flask import redirect
    chore = Chore.query.get_or_404(chore_id)
    db.session.delete(chore)
    db.session.commit()
    return redirect('/chores')

if __name__ == '__main__':
    app.run(debug=True)