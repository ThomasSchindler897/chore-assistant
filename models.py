from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()

class Completion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chore_id = db.Column(db.Integer, db.ForeignKey('chore.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.now)
    chore = db.relationship('Chore', backref=db.backref('completions', cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<Completion Chore {self.chore_id} at {self.completed_at}>'

class Chore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    priority = db.Column(db.Integer, default=1)  # 1-5
    completed = db.Column(db.Boolean, default=False)
    
    # New frequency fields
    frequency = db.Column(db.String(20), default='daily')  # daily, weekly, monthly, once
    frequency_details = db.Column(db.String(200))  # e.g., "Monday,Wednesday" or "2,15" for dates
    
    # Track when chore was last completed
    last_completed = db.Column(db.DateTime)
    start_date = db.Column(db.DateTime, default=datetime.now)  # Date when chore recurrence begins

    def is_due_today(self):
        """Check if this chore is due today based on frequency"""
        today = datetime.now()
        day_name = today.strftime('%A')
        day_of_month = today.day
        
        if self.frequency == 'daily':
            return True
        
        elif self.frequency == 'weekly':
            if self.frequency_details:
                days = [d.strip() for d in self.frequency_details.split(',')]
                return day_name in days
            return False
        
        elif self.frequency == 'monthly':
            if self.frequency_details:
                try:
                    due_day = int(self.frequency_details)
                    return day_of_month == due_day
                except ValueError:
                    return False
            return False
        
        elif self.frequency == 'once':
            return not self.completed
        
        return False
    
    def is_overdue(self):
        """Check if this chore is overdue (was due in the past and not completed)"""
        if self.completed or self.frequency == 'once':
            return False
        
        today = datetime.now()
        day_name = today.strftime('%A')
        day_of_month = today.day
        
        # For daily, it's never "overdue" in the traditional sense
        if self.frequency == 'daily':
            return False
        
        # For weekly, check if the due day has already passed this week
        elif self.frequency == 'weekly':
            if self.frequency_details:
                days = [d.strip() for d in self.frequency_details.split(',')]
                days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                
                # Check if any due day has passed this week
                for due_day in days:
                    if due_day in days_of_week:
                        due_day_index = days_of_week.index(due_day)
                        today_index = days_of_week.index(day_name)
                        if due_day_index < today_index:
                            return True
            return False
        
        # For monthly, check if the due date has passed this month
        elif self.frequency == 'monthly':
            if self.frequency_details:
                try:
                    due_day = int(self.frequency_details)
                    return due_day < day_of_month
                except ValueError:
                    return False
            return False
        
        return False
    
    def get_next_due_date(self):
        """Calculate and return the next due date as a string"""
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        day_name = today.strftime('%A')
        day_of_month = today.day
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        if self.frequency == 'daily':
            return "Daily"
        
        elif self.frequency == 'weekly':
            if self.frequency_details:
                due_days = [d.strip() for d in self.frequency_details.split(',')]
                
                # Check if tomorrow is a due day
                tomorrow_name = tomorrow.strftime('%A')
                if tomorrow_name in due_days:
                    return "Tomorrow"
                
                # Find next occurrence
                today_index = days_of_week.index(day_name)
                
                for i in range(1, 8):
                    check_date = today + timedelta(days=i)
                    check_day_name = check_date.strftime('%A')
                    if check_day_name in due_days:
                        return check_date.strftime('%a, %b %d')  # e.g., "Mon, Jul 29"
            return "Weekly"
        
        elif self.frequency == 'monthly':
            if self.frequency_details:
                try:
                    due_day = int(self.frequency_details)
                    if due_day == day_of_month:
                        return "Today"
                    elif due_day == tomorrow.day and tomorrow.month == today.month:
                        return "Tomorrow"
                    elif due_day > day_of_month:
                        # Same month
                        next_due = today.replace(day=due_day)
                        return next_due.strftime('%a, %b %d')
                    else:
                        # Next month
                        if today.month == 12:
                            next_due = today.replace(year=today.year + 1, month=1, day=due_day)
                        else:
                            next_due = today.replace(month=today.month + 1, day=due_day)
                        return next_due.strftime('%a, %b %d')
                except ValueError:
                    return "Monthly"
            return "Monthly"
        
        elif self.frequency == 'once':
            return "One-time" if not self.completed else "Completed"
        
        return "Unknown"
    
    def get_due_description(self):
        """Return a human-readable description of when this chore is due"""
        if self.frequency == 'daily':
            return "Every day"
        
        elif self.frequency == 'weekly':
            if self.frequency_details:
                return f"Every: {self.frequency_details}"
            return "Weekly"
        
        elif self.frequency == 'monthly':
            if self.frequency_details:
                # Format: "1st Friday, 4th Saturday"
                formatted = ', '.join([day.strip() for day in self.frequency_details.split(',')])
                return f"On the {formatted} of each month"
            return "Monthly"
        
        elif self.frequency == 'once':
            return "One-time task"
        
        return "Unknown"

    def get_completion_count(self):
        """Get total number of times this chore has been completed"""
        return len(self.completions)

    def get_completion_percentage(self):
        """Calculate completion percentage based on frequency"""
        from datetime import datetime, timedelta
    
        if self.frequency == 'daily':
            # Count completions in last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent = [c for c in self.completions if c.completed_at >= thirty_days_ago]
            return int((len(recent) / 30) * 100) if recent else 0
    
        elif self.frequency == 'weekly':
            # Count completions in last 12 weeks
            twelve_weeks_ago = datetime.now() - timedelta(weeks=12)
            recent = [c for c in self.completions if c.completed_at >= twelve_weeks_ago]
            return int((len(recent) / 12) * 100) if recent else 0
    
        elif self.frequency == 'monthly':
            # Count completions in last 12 months
            twelve_months_ago = datetime.now() - timedelta(days=365)
            recent = [c for c in self.completions if c.completed_at >= twelve_months_ago]
            return int((len(recent) / 12) * 100) if recent else 0
    
        return 0

    def get_current_streak(self):
        """Calculate current completion streak"""
        if not self.completions:
            return 0
    
        from datetime import datetime, timedelta
    
        # Sort completions by date (newest first)
        sorted_completions = sorted(self.completions, key=lambda x: x.completed_at, reverse=True)
    
        if self.frequency == 'daily':
            streak = 0
            expected_date = datetime.now().date()
        
            for completion in sorted_completions:
                completion_date = completion.completed_at.date()
                if completion_date == expected_date:
                    streak += 1
                    expected_date -= timedelta(days=1)
                else:
                    break
        
            return streak
    
        elif self.frequency == 'weekly':
            # Check if most recent completion was within last week
            most_recent = sorted_completions[0]
            if (datetime.now() - most_recent.completed_at).days <= 7:
                return len([c for c in sorted_completions if (datetime.now() - c.completed_at).days <= 7])
            return 0
    
        return 0

    def __repr__(self):
        return f'<Chore {self.name}>'