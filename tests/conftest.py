"""
Pytest configuration and fixtures for Chore Assistant tests.
Includes date mocking with freezegun for testing date-dependent logic.

This version supports both legacy (app) and new (setup_db) fixture styles.
"""

import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time
from models import db, Chore, Completion
from app import app as flask_app  # ← RENAMED: Import as flask_app to avoid naming conflict


# ============================================================================
# LEGACY FIXTURE (app) - For backward compatibility with existing tests
# ============================================================================

@pytest.fixture(scope='function')
def app():
    """Provide a test app - compatible with existing tests"""
    with flask_app.app_context():  # ← Now uses flask_app, not app
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


# ============================================================================
# NEW FIXTURE (setup_db) - For new-style tests
# ============================================================================

@pytest.fixture(scope='function')
def setup_db():
    """Create a clean database for each test"""
    with flask_app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


# ============================================================================
# SESSION FIXTURE - Database session access
# ============================================================================

@pytest.fixture(scope='function')
def session(app):
    """Provide database session for tests that need direct session access"""
    return db.session


# ============================================================================
# BASIC CHORES (No Completions)
# ============================================================================

@pytest.fixture
def daily_chore(app):
    """A simple daily chore with no completions"""
    chore = Chore(name="Test Daily Chore", frequency='daily')
    db.session.add(chore)
    db.session.commit()
    return chore


@pytest.fixture
def weekly_chore(app):
    """A simple weekly chore (Mondays, Wednesdays, and Fridays)"""
    chore = Chore(name="Test Weekly Chore", frequency='weekly', frequency_details='Monday,Wednesday,Friday')
    db.session.add(chore)
    db.session.commit()
    return chore


@pytest.fixture
def monthly_chore(app):
    """A simple monthly chore (15th of month)"""
    chore = Chore(name="Test Monthly Chore", frequency='monthly', frequency_details='15')
    db.session.add(chore)
    db.session.commit()
    return chore


@pytest.fixture
def once_chore(app):
    """A one-time chore"""
    chore = Chore(name="Test Once Chore", frequency='once')
    db.session.add(chore)
    db.session.commit()
    return chore


# ============================================================================
# CHORES WITH COMPLETIONS
# ============================================================================

@pytest.fixture
def daily_chore_with_completions(app):
    """Daily chore with 5 consecutive day completions.
    
    Creates completions for: Mon Jul 29, Tue Jul 30, Wed Jul 31, Thu Aug 1, Fri Aug 2
    """
    chore = Chore(name="Test Daily Chore", frequency='daily')
    db.session.add(chore)
    db.session.flush()
    
    # Create 5 consecutive day completions using explicit datetime objects
    completion_dates = [
        datetime(2024, 7, 29, 10, 0, 0),  # Monday
        datetime(2024, 7, 30, 10, 0, 0),  # Tuesday
        datetime(2024, 7, 31, 10, 0, 0),  # Wednesday
        datetime(2024, 8, 1, 10, 0, 0),   # Thursday
        datetime(2024, 8, 2, 10, 0, 0),   # Friday
    ]
    
    for comp_date in completion_dates:
        completion = Completion(chore_id=chore.id, completed_at=comp_date)
        db.session.add(completion)
    
    db.session.commit()
    return chore


@pytest.fixture
def incomplete_daily_chore_with_gap(app):
    """Daily chore with completions but with a gap (broken streak).
    
    Creates completions for: Mon Jul 29, Tue Jul 30
    Then a gap (no completion on Wed Jul 31)
    Then: Thu Aug 1, Fri Aug 2
    """
    chore = Chore(name="Test Daily Chore", frequency='daily')
    db.session.add(chore)
    db.session.flush()
    
    # Create completions with a gap on Wed Jul 31
    completion_dates = [
        datetime(2024, 7, 29, 10, 0, 0),  # Monday - completed
        datetime(2024, 7, 30, 10, 0, 0),  # Tuesday - completed
        # NOTE: Wednesday (2024-07-31) is intentionally skipped (gap)
        datetime(2024, 8, 1, 10, 0, 0),   # Thursday - completed
        datetime(2024, 8, 2, 10, 0, 0),   # Friday - completed
    ]
    
    for comp_date in completion_dates:
        completion = Completion(chore_id=chore.id, completed_at=comp_date)
        db.session.add(completion)
    
    db.session.commit()
    return chore


@pytest.fixture
def weekly_chore_with_completions(app):
    """Weekly chore (Mondays only) with recent completions"""
    chore = Chore(name="Test Weekly Chore", frequency='weekly', frequency_details='Monday')
    db.session.add(chore)
    db.session.flush()
    
    # Add completions for recent Mondays (within 7 days)
    base_date = datetime(2024, 7, 29, 10, 0, 0)  # Monday
    
    completion1 = Completion(chore_id=chore.id, completed_at=base_date)
    completion2 = Completion(chore_id=chore.id, completed_at=base_date + timedelta(weeks=1))
    
    db.session.add_all([completion1, completion2])
    db.session.commit()
    return chore


@pytest.fixture
def monthly_chore_with_completions(app):
    """Monthly chore (15th) with recent completions"""
    chore = Chore(name="Test Monthly Chore", frequency='monthly', frequency_details='15')
    db.session.add(chore)
    db.session.flush()
    
    # Add completions for the 15th of recent months
    completion1 = Completion(chore_id=chore.id, completed_at=datetime(2024, 6, 15, 10, 0, 0))
    completion2 = Completion(chore_id=chore.id, completed_at=datetime(2024, 7, 15, 10, 0, 0))
    
    db.session.add_all([completion1, completion2])
    db.session.commit()
    return chore


# ============================================================================
# EDGE CASE CHORES
# ============================================================================

@pytest.fixture
def monthly_chore_31st(app):
    """Monthly chore on the 31st (for testing Feb edge case)"""
    chore = Chore(name="Test Monthly 31st", frequency='monthly', frequency_details='31')
    db.session.add(chore)
    db.session.commit()
    return chore


@pytest.fixture
def monthly_chore_29th(app):
    """Monthly chore on the 29th (leap year testing)"""
    chore = Chore(name="Test Monthly 29th", frequency='monthly', frequency_details='29')
    db.session.add(chore)
    db.session.commit()
    return chore


@pytest.fixture
def completed_chore(app):
    """A completed one-time chore"""
    chore = Chore(name="Completed Once Chore", frequency='once', completed=True)
    db.session.add(chore)
    db.session.commit()
    return chore


# ============================================================================
# MULTIPLE CHORES FOR LISTING TESTS
# ============================================================================

@pytest.fixture
def multiple_chores(app):
    """Multiple chores of different frequencies"""
    chores = [
        Chore(name="Daily Task", frequency='daily', priority=5),
        Chore(name="Weekly Task", frequency='weekly', frequency_details='Monday,Friday', priority=3),
        Chore(name="Monthly Task", frequency='monthly', frequency_details='1', priority=2),
        Chore(name="One-time Task", frequency='once', priority=1),
    ]
    db.session.add_all(chores)
    db.session.commit()
    return chores


# ============================================================================
# ROUTE TESTING FIXTURES
# ============================================================================

@pytest.fixture
def client(app):
    """Provide a test client for route testing"""
    return app.test_client()


@pytest.fixture
def session(app):
    """Provide direct access to the database session for tests"""
    return db.session


# ============================================================================
# FREEZEGUN CONTEXT FOR DATE TESTING
# ============================================================================

@pytest.fixture
def frozen_monday():
    """Freeze time to Monday, July 29, 2024"""
    with freeze_time("2024-07-29"):
        yield datetime(2024, 7, 29)


@pytest.fixture
def frozen_friday():
    """Freeze time to Friday, August 2, 2024"""
    with freeze_time("2024-08-02"):
        yield datetime(2024, 8, 2)


@pytest.fixture
def frozen_weekday():
    """Freeze time to Wednesday, July 31, 2024"""
    with freeze_time("2024-07-31"):
        yield datetime(2024, 7, 31)