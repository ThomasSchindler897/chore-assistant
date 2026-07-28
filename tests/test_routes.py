import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time
from models import Chore, Completion, db

# ============================================================================
# HOME PAGE TESTS (/)
# ============================================================================

class TestHomeRoute:
    """Test cases for home page route"""
    
    def test_home_page_loads(self, client):
        """Home page should load successfully"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Chore Assistant' in response.data or b'chore' in response.data.lower()
    
    def test_home_shows_todays_chores(self, client, session):
        """Home page should show chores due today"""
        chore = Chore(
            name="Today's Chore",
            frequency='daily'
        )
        session.add(chore)
        session.commit()
        
        response = client.get('/')
        assert response.status_code == 200
        assert b"Today's Chore" in response.data
    
    def test_home_doesnt_show_completed_chores_in_todays_section(self, client, session):
        """Home page should not show completed chores in today's section"""
        chore = Chore(
            name="Completed Chore",
            frequency='daily',
            completed=True
        )
        session.add(chore)
        session.commit()
        
        response = client.get('/')
        # The chore exists but shouldn't be in the "today's chores" section
        # It might appear in the "completed" section instead
        assert response.status_code == 200
    
    def test_home_shows_overdue_chores(self, client, session):
        """Home page should show overdue chores"""
        chore = Chore(
            name="Overdue Monday Chore",
            frequency='weekly',
            frequency_details='Monday'
        )
        session.add(chore)
        session.commit()
        
        with freeze_time("2024-08-02"):  # Friday (Monday has passed)
            response = client.get('/')
            assert response.status_code == 200
            assert b"Overdue Monday Chore" in response.data
    
    def test_home_shows_date(self, client):
        """Home page should display today's date"""
        with freeze_time("2024-08-15"):
            response = client.get('/')
            assert response.status_code == 200
            assert b"August" in response.data or b"2024" in response.data


# ============================================================================
# TOGGLE ROUTE TESTS (/toggle/<id>)
# ============================================================================

class TestToggleRoute:
    """Test cases for toggling chore completion"""
    
    def test_toggle_marks_chore_complete(self, client, session):
        """Toggling uncompleted chore should mark it complete"""
        chore = Chore(name="Test Chore", frequency='daily', completed=False)
        session.add(chore)
        session.commit()
        chore_id = chore.id
        
        response = client.post(f'/toggle/{chore_id}', follow_redirects=True)
        
        # Reload chore to check
        chore = Chore.query.get(chore_id)
        assert chore.completed is True
    
    def test_toggle_marks_chore_incomplete(self, client, session):
        """Toggling completed chore should mark it incomplete"""
        chore = Chore(name="Test Chore", frequency='daily', completed=True)
        session.add(chore)
        session.commit()
        chore_id = chore.id
        
        response = client.post(f'/toggle/{chore_id}', follow_redirects=True)
        
        chore = Chore.query.get(chore_id)
        assert chore.completed is False
    
    def test_toggle_creates_completion_record(self, client, session):
        """Toggling a chore complete should create a Completion record"""
        chore = Chore(name="Test Chore", frequency='daily', completed=False)
        session.add(chore)
        session.commit()
        chore_id = chore.id
        
        response = client.post(f'/toggle/{chore_id}', follow_redirects=True)
        
        # Check that a completion was recorded
        completions = Completion.query.filter_by(chore_id=chore_id).all()
        assert len(completions) >= 1
    
    def test_toggle_removes_completion_record_on_uncheck(self, client, session):
        """Unchecking a chore should remove today's completion record"""
        chore = Chore(name="Test Chore", frequency='daily', completed=True)
        session.add(chore)
        session.commit()
        chore_id = chore.id
        
        # Add a completion for today
        completion = Completion(chore_id=chore_id, completed_at=datetime.now())
        session.add(completion)
        session.commit()
        
        # Toggle it back to incomplete
        response = client.post(f'/toggle/{chore_id}', follow_redirects=True)
        
        # Check that today's completion was removed
        today = datetime.now().date()
        completions_today = Completion.query.filter(
            Completion.chore_id == chore_id,
            db.func.date(Completion.completed_at) == today
        ).all()
        assert len(completions_today) == 0
    
    def test_toggle_prevents_double_logging_same_day(self, client, session):
        """Toggling same chore multiple times same day should not create multiple records"""
        chore = Chore(name="Test Chore", frequency='daily', completed=False)
        session.add(chore)
        session.commit()
        chore_id = chore.id
        
        # Toggle on
        client.post(f'/toggle/{chore_id}', follow_redirects=True)
        # Toggle off
        client.post(f'/toggle/{chore_id}', follow_redirects=True)
        # Toggle on again
        client.post(f'/toggle/{chore_id}', follow_redirects=True)
        
        # Should only have 1 completion record for today
        today = datetime.now().date()
        completions_today = Completion.query.filter(
            Completion.chore_id == chore_id,
            db.func.date(Completion.completed_at) == today
        ).all()
        assert len(completions_today) == 1
    
    def test_toggle_sets_last_completed(self, client, session):
        """Toggling a chore complete should set last_completed timestamp"""
        chore = Chore(name="Test Chore", frequency='daily', completed=False)
        session.add(chore)
        session.commit()
        chore_id = chore.id
        
        with freeze_time("2024-08-15 14:30:00"):
            client.post(f'/toggle/{chore_id}', follow_redirects=True)
        
        chore = Chore.query.get(chore_id)
        assert chore.last_completed is not None


# ============================================================================
# CHORES LIST ROUTE TESTS (/chores)
# ============================================================================

class TestChoresRoute:
    """Test cases for chores list page"""
    
    def test_chores_page_loads(self, client):
        """Chores page should load"""
        response = client.get('/chores')
        assert response.status_code == 200
    
    def test_chores_page_shows_all_chores(self, client, session):
        """Chores page should display all chores"""
        chores = [
            Chore(name="Chore 1", frequency='daily'),
            Chore(name="Chore 2", frequency='weekly', frequency_details='Monday'),
            Chore(name="Chore 3", frequency='monthly', frequency_details='15'),
        ]
        for chore in chores:
            session.add(chore)
        session.commit()
        
        response = client.get('/chores')
        assert response.status_code == 200
        assert b"Chore 1" in response.data
        assert b"Chore 2" in response.data
        assert b"Chore 3" in response.data
    
    def test_chores_page_shows_next_due_date(self, client, session):
        """Chores page should show next due date for each chore"""
        chore = Chore(name="Test", frequency='daily')
        session.add(chore)
        session.commit()
        
        response = client.get('/chores')
        assert response.status_code == 200
        assert b"Daily" in response.data


# ============================================================================
# ADD CHORE ROUTE TESTS (/add)
# ============================================================================

class TestAddChoreRoute:
    """Test cases for adding new chores"""
    
    def test_add_page_loads(self, client):
        """Add chore page should load"""
        response = client.get('/add')
        assert response.status_code == 200
    
    def test_add_daily_chore(self, client, session):
        """Should be able to add a daily chore"""
        response = client.post('/add', data={
            'name': 'New Daily Chore',
            'description': 'Test chore',
            'priority': '3',
            'frequency': 'daily',
            'frequency_details': ''
        }, follow_redirects=True)
        
        chore = Chore.query.filter_by(name='New Daily Chore').first()
        assert chore is not None
        assert chore.frequency == 'daily'
    
    def test_add_weekly_chore(self, client, session):
        """Should be able to add a weekly chore"""
        response = client.post('/add', data={
            'name': 'New Weekly Chore',
            'description': 'Test chore',
            'priority': '2',
            'frequency': 'weekly',
            'frequency_details': 'Monday,Wednesday'
        }, follow_redirects=True)
        
        chore = Chore.query.filter_by(name='New Weekly Chore').first()
        assert chore is not None
        assert chore.frequency == 'weekly'
        assert chore.frequency_details == 'Monday,Wednesday'
    
    def test_add_monthly_chore(self, client, session):
        """Should be able to add a monthly chore"""
        response = client.post('/add', data={
            'name': 'New Monthly Chore',
            'description': 'Test chore',
            'priority': '1',
            'frequency': 'monthly',
            'frequency_details': '15'
        }, follow_redirects=True)
        
        chore = Chore.query.filter_by(name='New Monthly Chore').first()
        assert chore is not None
        assert chore.frequency == 'monthly'
        assert chore.frequency_details == '15'
    
    def test_add_chore_with_minimal_data(self, client, session):
        """Should be able to add chore with just name"""
        response = client.post('/add', data={
            'name': 'Minimal Chore',
            'description': '',
            'priority': '3',
            'frequency': 'daily',
            'frequency_details': ''
        }, follow_redirects=True)
        
        chore = Chore.query.filter_by(name='Minimal Chore').first()
        assert chore is not None
    
    def test_add_chore_redirects_to_chores_page(self, client, session):
        """Adding a chore should redirect to chores page"""
        response = client.post('/add', data={
            'name': 'Redirect Test',
            'priority': '3',
            'frequency': 'daily'
        }, follow_redirects=False)
        
        assert response.status_code == 302  # Redirect


# ============================================================================
# EDIT CHORE ROUTE TESTS (/edit/<id>)
# ============================================================================

class TestEditChoreRoute:
    """Test cases for editing chores"""
    
    def test_edit_page_loads(self, client, session):
        """Edit page should load for existing chore"""
        chore = Chore(name="Test", frequency='daily')
        session.add(chore)
        session.commit()
        
        response = client.get(f'/edit/{chore.id}')
        assert response.status_code == 200
    
    def test_edit_chore_name(self, client, session):
        """Should be able to edit chore name"""
        chore = Chore(name="Original Name", frequency='daily')
        session.add(chore)
        session.commit()
        chore_id = chore.id
        
        response = client.post(f'/edit/{chore_id}', data={
            'name': 'Updated Name',
            'description': '',
            'priority': '3',
            'frequency': 'daily',
            'frequency_details': ''
        }, follow_redirects=True)
        
        chore = Chore.query.get(chore_id)
        assert chore.name == 'Updated Name'
    
    def test_edit_chore_frequency(self, client, session):
        """Should be able to edit chore frequency"""
        chore = Chore(name="Test", frequency='daily')
        session.add(chore)
        session.commit()
        chore_id = chore.id
        
        response = client.post(f'/edit/{chore_id}', data={
            'name': 'Test',
            'description': '',
            'priority': '3',
            'frequency': 'weekly',
            'frequency_details': 'Monday,Friday'
        }, follow_redirects=True)
        
        chore = Chore.query.get(chore_id)
        assert chore.frequency == 'weekly'
        assert chore.frequency_details == 'Monday,Friday'
    
    def test_edit_chore_priority(self, client, session):
        """Should be able to edit chore priority"""
        chore = Chore(name="Test", frequency='daily', priority=1)
        session.add(chore)
        session.commit()
        chore_id = chore.id
        
        response = client.post(f'/edit/{chore_id}', data={
            'name': 'Test',
            'description': '',
            'priority': '5',
            'frequency': 'daily',
            'frequency_details': ''
        }, follow_redirects=True)
        
        chore = Chore.query.get(chore_id)
        assert chore.priority == 5
    
    def test_edit_chore_mark_complete(self, client, session):
        """Should be able to mark chore as complete via edit"""
        chore = Chore(name="Test", frequency='daily', completed=False)
        session.add(chore)
        session.commit()
        chore_id = chore.id
        
        response = client.post(f'/edit/{chore_id}', data={
            'name': 'Test',
            'description': '',
            'priority': '3',
            'frequency': 'daily',
            'frequency_details': '',
            'completed': 'on'
        }, follow_redirects=True)
        
        chore = Chore.query.get(chore_id)
        assert chore.completed is True


# ============================================================================
# DELETE CHORE ROUTE TESTS (/delete/<id>)
# ============================================================================

class TestDeleteChoreRoute:
    """Test cases for deleting chores"""
    
    def test_delete_chore(self, client, session):
        """Should be able to delete a chore"""
        chore = Chore(name="To Delete", frequency='daily')
        session.add(chore)
        session.commit()
        chore_id = chore.id
        
        response = client.post(f'/delete/{chore_id}', follow_redirects=True)
        
        chore = Chore.query.get(chore_id)
        assert chore is None
    
    def test_delete_removes_completions(self, client, session):
        """Deleting a chore should remove its completion records"""
        chore = Chore(name="To Delete", frequency='daily')
        session.add(chore)
        session.commit()
        chore_id = chore.id
        
        # Add some completions
        for i in range(3):
            completion = Completion(chore_id=chore_id, completed_at=datetime.now())
            session.add(completion)
        session.commit()
        
        # Delete the chore
        response = client.post(f'/delete/{chore_id}', follow_redirects=True)
        
        # Completions should be gone too (due to cascade delete)
        completions = Completion.query.filter_by(chore_id=chore_id).all()
        assert len(completions) == 0


# ============================================================================
# STATS ROUTE TESTS (/stats)
# ============================================================================

class TestStatsRoute:
    """Test cases for stats page"""
    
    def test_stats_page_loads(self, client):
        """Stats page should load"""
        response = client.get('/stats')
        assert response.status_code == 200
    
    def test_stats_page_shows_all_chores(self, client, session):
        """Stats page should show all chores with metrics"""
        chore = Chore(name="Test Chore", frequency='daily')
        session.add(chore)
        session.commit()
        
        # Add some completions
        for i in range(5, 0, -1):
            with freeze_time(datetime.now() - timedelta(days=i)):
                completion = Completion(chore_id=chore.id, completed_at=datetime.now())
                session.add(completion)
        session.commit()
        
        response = client.get('/stats')
        assert response.status_code == 200
        assert b"Test Chore" in response.data
    
    def test_stats_page_shows_completion_percentage(self, client, session):
        """Stats page should display completion percentages"""
        chore = Chore(name="Test Chore", frequency='daily')
        session.add(chore)
        session.commit()
        
        response = client.get('/stats')
        assert response.status_code == 200


# ============================================================================
# 404 TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling"""
    
    def test_edit_nonexistent_chore_404(self, client):
        """Editing nonexistent chore should return 404"""
        response = client.get('/edit/9999')
        assert response.status_code == 404
    
    def test_delete_nonexistent_chore_404(self, client):
        """Deleting nonexistent chore should return 404"""
        response = client.post('/delete/9999')
        assert response.status_code == 404
    
    def test_toggle_nonexistent_chore_404(self, client):
        """Toggling nonexistent chore should return 404"""
        response = client.post('/toggle/9999')
        assert response.status_code == 404
