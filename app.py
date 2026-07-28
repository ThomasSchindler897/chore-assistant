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
    from datetime import datetime, timedelta
    
    all_chores = Chore.query.all()
    
    # Calculate stats for each chore
    chore_stats = []
    for chore in all_chores:
        chore_stats.append({
            'chore': chore,
            'streak': chore.get_current_streak(),
            'completion_rate': chore.get_completion_percentage(),
            'total_completions': chore.get_completion_count(),
            'frequency': chore.get_due_description()
        })
    
    # Calculate overall stats
    total_completions = sum(c['total_completions'] for c in chore_stats)
    avg_completion_rate = sum(c['completion_rate'] for c in chore_stats) / len(chore_stats) if chore_stats else 0
    total_streaks = sum(c['streak'] for c in chore_stats)
    
    # Get monthly completion data (last 6 months)
    monthly_data = {}
    for i in range(6, -1, -1):
        month_date = datetime.now() - timedelta(days=30*i)
        month_key = month_date.strftime('%b %Y')
        monthly_completions = 0
        
        for chore in all_chores:
            for completion in chore.completions:
                if (completion.completed_at.year == month_date.year and 
                    completion.completed_at.month == month_date.month):
                    monthly_completions += 1
        
        monthly_data[month_key] = monthly_completions
    
    # Achievement badges logic
    badges = []
    if total_completions >= 10:
        badges.append({'name': 'Getting Started', 'icon': '🚀', 'desc': '10+ completions'})
    if total_completions >= 50:
        badges.append({'name': 'On a Roll', 'icon': '🔥', 'desc': '50+ completions'})
    if total_completions >= 100:
        badges.append({'name': 'Champion', 'icon': '👑', 'desc': '100+ completions'})
    if avg_completion_rate >= 75:
        badges.append({'name': 'Consistent', 'icon': '⭐', 'desc': '75%+ completion rate'})
    if total_streaks >= 10:
        badges.append({'name': 'Streak Master', 'icon': '💪', 'desc': '10+ day streak'})
    
    return render_template('stats.html',
                         chores=all_chores,
                         chore_stats=chore_stats,
                         total_completions=total_completions,
                         avg_completion_rate=avg_completion_rate,
                         total_streaks=total_streaks,
                         monthly_data=monthly_data,
                         badges=badges)

@app.route('/delete/<int:chore_id>', methods=['POST'])
def delete_chore(chore_id):
    from flask import redirect
    chore = Chore.query.get_or_404(chore_id)
    db.session.delete(chore)
    db.session.commit()
    return redirect('/chores')

@app.route('/calendar')
def calendar():
    from datetime import datetime, timedelta
    import calendar as cal
    
    # Get current month/year and view type
    today = datetime.now()
    year = int(request.args.get('year', today.year))
    month = int(request.args.get('month', today.month))
    view = request.args.get('view', 'monthly')  # 'monthly' or 'weekly'
    
    # Get all chores
    all_chores = Chore.query.all()
    
    # Calculate overdue chores
    overdue_chores = [chore for chore in all_chores if chore.is_overdue()]
    
    # Calculate upcoming chores (next 7 days)
    upcoming_chores = []
    for i in range(1, 8):
        future_date = today + timedelta(days=i)
        future_date_str = future_date.strftime('%A')
        
        for chore in all_chores:
            if chore.completed or chore.frequency == 'once':
                continue
            
            if chore.frequency == 'daily':
                upcoming_chores.append({'chore': chore, 'date': future_date, 'days_away': i})
            elif chore.frequency == 'weekly' and chore.frequency_details:
                due_days = [d.strip() for d in chore.frequency_details.split(',')]
                if future_date_str in due_days:
                    upcoming_chores.append({'chore': chore, 'date': future_date, 'days_away': i})
            elif chore.frequency == 'monthly' and chore.frequency_details:
                try:
                    due_day = int(chore.frequency_details)
                    if future_date.day == due_day:
                        upcoming_chores.append({'chore': chore, 'date': future_date, 'days_away': i})
                except ValueError:
                    pass
    
    # Build calendar data
    calendar_days = cal.monthcalendar(year, month)
    month_name = cal.month_name[month]
    
    # Map chores to days
    chores_by_day = {}
    for day_row in calendar_days:
        for day in day_row:
            if day == 0:
                continue
            chores_today = []
            test_date = datetime(year, month, day)
            test_date_str = test_date.strftime('%A')
            
            for chore in all_chores:
                if chore.frequency == 'daily':
                    chores_today.append(chore)
                elif chore.frequency == 'weekly' and chore.frequency_details:
                    due_days = [d.strip() for d in chore.frequency_details.split(',')]
                    if test_date_str in due_days:
                        chores_today.append(chore)
                elif chore.frequency == 'monthly' and chore.frequency_details:
                    try:
                        due_day = int(chore.frequency_details)
                        if day == due_day:
                            chores_today.append(chore)
                    except ValueError:
                        pass
            
            chores_by_day[day] = chores_today
    
    # Navigation
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    return render_template('calendar.html',
                         year=year,
                         month=month,
                         month_name=month_name,
                         calendar_days=calendar_days,
                         chores_by_day=chores_by_day,
                         prev_year=prev_year,
                         prev_month=prev_month,
                         next_year=next_year,
                         next_month=next_month,
                         today=today,
                         overdue_chores=overdue_chores,
                         upcoming_chores=upcoming_chores,
                         view=view)

if __name__ == '__main__':
    app.run(debug=True)