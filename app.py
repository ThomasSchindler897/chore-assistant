from flask import Flask, render_template, request, redirect
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