import pytest
from datetime import datetime, timedelta, date
from freezegun import freeze_time
from models import Chore, Completion, db

# ============================================================================
# DAILY CHORE TESTS
# ============================================================================

class TestDailyChore:
    """Test cases for daily frequency chores"""
    
    def test_daily_is_due_today(self, daily_chore):
        """Daily chore should be due every day"""
        assert daily_chore.is_due_today() is True
    
    def test_daily_next_due_date_is_daily(self, daily_chore):
        """Daily chore should always return 'Daily' as next due date"""
        assert daily_chore.get_next_due_date() == "Daily"
    
    def test_daily_is_never_overdue(self, daily_chore):
        """Daily chores are never considered overdue"""
        assert daily_chore.is_overdue() is False
    
    def test_daily_not_overdue_even_if_uncompleted(self, daily_chore):
        """Daily chore should not be overdue even if not completed"""
        daily_chore.completed = False
        assert daily_chore.is_overdue() is False
    
    def test_daily_completion_percentage_30_days(self, session):
        """Daily chore should calculate completion % based on 30-day window"""
        chore = Chore(
            name="Daily",
            frequency='daily',
            frequency_details=None
        )
        session.add(chore)
        session.commit()
        
        # Add 15 completions in the last 30 days
        from datetime import datetime, timedelta
        for i in range(15, 0, -1):
            with freeze_time(datetime.now() - timedelta(days=i)):
                completion = Completion(chore_id=chore.id, completed_at=datetime.now())
                session.add(completion)
        session.commit()
        
        # 15/30 = 50%
        assert chore.get_completion_percentage() == 50
    
    def test_daily_completion_percentage_all_days(self, session):
        """Daily chore with 30 completions should be 100%"""
        chore = Chore(
            name="Perfect Daily",
            frequency='daily',
            frequency_details=None
        )
        session.add(chore)
        session.commit()
        
        # Add 30 completions in the last 30 days
        from datetime import datetime, timedelta
        for i in range(30, 0, -1):
            with freeze_time(datetime.now() - timedelta(days=i)):
                completion = Completion(chore_id=chore.id, completed_at=datetime.now())
                session.add(completion)
        session.commit()
        
        assert chore.get_completion_percentage() == 100
    
    def test_daily_streak_5_consecutive_days(self, daily_chore_with_completions):
        """Daily chore with 5 consecutive completions should have streak of 5"""
        with freeze_time("2024-08-02"):  # Freeze on day after last completion
            streak = daily_chore_with_completions.get_current_streak()
            assert streak == 5
    
    def test_daily_streak_broken_by_gap(self, incomplete_daily_chore_with_gap):
        """Streak should break if a day is missed"""
        with freeze_time("2024-08-02"):  # Current day
            # Last completion was 1 day ago, but there's a gap before that
            streak = incomplete_daily_chore_with_gap.get_current_streak()
            assert streak == 2  # Only counts current streak, which is just 2 days


# ============================================================================
# WEEKLY CHORE TESTS
# ============================================================================

class TestWeeklyChore:
    """Test cases for weekly frequency chores"""
    
    def test_weekly_due_on_specified_days(self, weekly_chore):
        """Weekly chore should be due on specified days only"""
        # weekly_chore is set to Monday, Wednesday, Friday
        
        with freeze_time("2024-07-29"):  # Monday
            assert weekly_chore.is_due_today() is True
        
        with freeze_time("2024-07-30"):  # Tuesday
            assert weekly_chore.is_due_today() is False
        
        with freeze_time("2024-07-31"):  # Wednesday
            assert weekly_chore.is_due_today() is True
        
        with freeze_time("2024-08-02"):  # Friday
            assert weekly_chore.is_due_today() is True
    
    def test_weekly_not_due_on_other_days(self, session):
        """Weekly chore should not be due on days not specified"""
        chore = Chore(
            name="Monday Only",
            frequency='weekly',
            frequency_details='Monday'
        )
        session.add(chore)
        session.commit()
        
        with freeze_time("2024-07-30"):  # Tuesday
            assert chore.is_due_today() is False
        
        with freeze_time("2024-07-31"):  # Wednesday
            assert chore.is_due_today() is False
    
    def test_weekly_overdue_if_day_passed_this_week(self, session):
        """Weekly chore should be overdue if its day already passed this week"""
        chore = Chore(
            name="Monday Chore",
            frequency='weekly',
            frequency_details='Monday'
        )
        session.add(chore)
        session.commit()
        
        # On Wednesday, Monday has already passed this week
        with freeze_time("2024-07-31"):  # Wednesday
            assert chore.is_overdue() is True
        
        # On Monday itself, not overdue
        with freeze_time("2024-07-29"):  # Monday
            assert chore.is_overdue() is False
    
    def test_weekly_not_overdue_if_day_hasnt_happened_yet(self, session):
        """Weekly chore should not be overdue if its day hasn't happened yet this week"""
        chore = Chore(
            name="Friday Chore",
            frequency='weekly',
            frequency_details='Friday'
        )
        session.add(chore)
        session.commit()
        
        with freeze_time("2024-07-29"):  # Monday (Friday hasn't happened)
            assert chore.is_overdue() is False
    
    def test_weekly_next_due_tomorrow(self, session):
        """Weekly chore should show 'Tomorrow' if due tomorrow"""
        chore = Chore(
            name="Tuesday Chore",
            frequency='weekly',
            frequency_details='Tuesday'
        )
        session.add(chore)
        session.commit()
        
        with freeze_time("2024-07-29"):  # Monday, Tuesday is tomorrow
            assert chore.get_next_due_date() == "Tomorrow"
    
    def test_weekly_next_due_formatted_date(self, session):
        """Weekly chore should format date properly for future dates"""
        chore = Chore(
            name="Friday Chore",
            frequency='weekly',
            frequency_details='Friday'
        )
        session.add(chore)
        session.commit()
        
        with freeze_time("2024-07-29"):  # Monday
            next_date = chore.get_next_due_date()
            assert next_date == "Fri, Aug 02"  # Friday is 4 days away
    
    def test_weekly_completion_percentage_12_weeks(self, session):
        """Weekly chore should calculate completion % based on 12-week window"""
        chore = Chore(
            name="Weekly",
            frequency='weekly',
            frequency_details='Monday'
        )
        session.add(chore)
        session.commit()
        
        # Add 6 completions in last 12 weeks
        from datetime import datetime, timedelta
        for i in range(6, 0, -1):
            with freeze_time(datetime.now() - timedelta(weeks=i)):
                completion = Completion(chore_id=chore.id, completed_at=datetime.now())
                session.add(completion)
        session.commit()
        
        # 6/12 = 50%
        assert chore.get_completion_percentage() == 50
    
    def test_weekly_streak_based_on_recent_completion(self, session):
        """Weekly chore streak should count completions within last 7 days if recent"""
        chore = Chore(
            name="Weekly",
            frequency='weekly',
            frequency_details='Monday'
        )
        session.add(chore)
        session.commit()
        
        with freeze_time("2024-08-05"):
            # Add 3 completions within last 7 days
            for i in range(3, 0, -1):
                with freeze_time(datetime.now() - timedelta(days=i)):
                    completion = Completion(chore_id=chore.id, completed_at=datetime.now())
                    session.add(completion)
            session.commit()
            
            streak = chore.get_current_streak()
            assert streak == 3
    
    def test_weekly_streak_zero_if_old_completion(self, session):
        """Weekly streak should be 0 if last completion was more than 7 days ago"""
        chore = Chore(
            name="Weekly",
            frequency='weekly',
            frequency_details='Monday'
        )
        session.add(chore)
        session.commit()
        
        with freeze_time("2024-08-05"):
            # Add completion 10 days ago
            with freeze_time(datetime.now() - timedelta(days=10)):
                completion = Completion(chore_id=chore.id, completed_at=datetime.now())
                session.add(completion)
            session.commit()
            
            streak = chore.get_current_streak()
            assert streak == 0


# ============================================================================
# MONTHLY CHORE TESTS
# ============================================================================

class TestMonthlyChore:
    """Test cases for monthly frequency chores"""
    
    def test_monthly_due_on_specified_day(self, monthly_chore):
        """Monthly chore should be due on specified day of month"""
        # monthly_chore is set to 15th
        
        with freeze_time("2024-08-15"):  # 15th
            assert monthly_chore.is_due_today() is True
        
        with freeze_time("2024-08-14"):  # 14th
            assert monthly_chore.is_due_today() is False
        
        with freeze_time("2024-08-16"):  # 16th
            assert monthly_chore.is_due_today() is False
    
    def test_monthly_overdue_if_day_passed_this_month(self, session):
        """Monthly chore should be overdue if its day already passed this month"""
        chore = Chore(
            name="15th Chore",
            frequency='monthly',
            frequency_details='15'
        )
        session.add(chore)
        session.commit()
        
        with freeze_time("2024-08-20"):  # 20th (15th has passed)
            assert chore.is_overdue() is True
        
        with freeze_time("2024-08-15"):  # 15th itself
            assert chore.is_overdue() is False
        
        with freeze_time("2024-08-10"):  # 10th (15th hasn't happened)
            assert chore.is_overdue() is False
    
    def test_monthly_next_due_today(self, session):
        """Monthly chore should show 'Today' if due today"""
        chore = Chore(
            name="15th Chore",
            frequency='monthly',
            frequency_details='15'
        )
        session.add(chore)
        session.commit()
        
        with freeze_time("2024-08-15"):
            assert chore.get_next_due_date() == "Today"
    
    def test_monthly_next_due_tomorrow(self, session):
        """Monthly chore should show 'Tomorrow' if due tomorrow"""
        chore = Chore(
            name="16th Chore",
            frequency='monthly',
            frequency_details='16'
        )
        session.add(chore)
        session.commit()
        
        with freeze_time("2024-08-15"):
            assert chore.get_next_due_date() == "Tomorrow"
    
    def test_monthly_next_due_later_this_month(self, session):
        """Monthly chore should format date for later this month"""
        chore = Chore(
            name="25th Chore",
            frequency='monthly',
            frequency_details='25'
        )
        session.add(chore)
        session.commit()
        
        with freeze_time("2024-08-15"):
            assert chore.get_next_due_date() == "Sun, Aug 25"
    
    def test_monthly_next_due_next_month(self, session):
        """Monthly chore should show next month's date if past due date this month"""
        chore = Chore(
            name="10th Chore",
            frequency='monthly',
            frequency_details='10'
        )
        session.add(chore)
        session.commit()
        
        with freeze_time("2024-08-15"):  # 15th (10th has passed)
            next_date = chore.get_next_due_date()
            # Should be September 10th
            assert "Sep" in next_date
    
    def test_monthly_next_due_next_year_december(self, session):
        """Monthly chore in December should show next year's date"""
        chore = Chore(
            name="10th Chore",
            frequency='monthly',
            frequency_details='10'
        )
        session.add(chore)
        session.commit()
        
        with freeze_time("2024-12-15"):  # December 15th
            next_date = chore.get_next_due_date()
            # Should be January 10th 2025
            assert "Jan" in next_date
    
    def test_monthly_completion_percentage_12_months(self, session):
        """Monthly chore should calculate completion % based on 12-month window"""
        chore = Chore(
            name="Monthly",
            frequency='monthly',
            frequency_details='15'
        )
        session.add(chore)
        session.commit()
        
        # Add 6 completions in last 12 months
        from datetime import datetime, timedelta
        for i in range(6, 0, -1):
            with freeze_time(datetime.now() - timedelta(days=30*i)):
                completion = Completion(chore_id=chore.id, completed_at=datetime.now())
                session.add(completion)
        session.commit()
        
        # 6/12 = 50%
        assert chore.get_completion_percentage() == 50


# ============================================================================
# ONCE CHORE TESTS
# ============================================================================

class TestOnceChore:
    """Test cases for one-time chores"""
    
    def test_once_is_due_if_not_completed(self, once_chore):
        """One-time chore should be due if not completed"""
        once_chore.completed = False
        assert once_chore.is_due_today() is True
    
    def test_once_not_due_if_completed(self, once_chore):
        """One-time chore should not be due if already completed"""
        once_chore.completed = True
        assert once_chore.is_due_today() is False
    
    def test_once_never_overdue(self, once_chore):
        """One-time chore should never be overdue"""
        assert once_chore.is_overdue() is False
    
    def test_once_next_due_shows_one_time(self, once_chore):
        """One-time chore should show 'One-time'"""
        once_chore.completed = False
        assert once_chore.get_next_due_date() == "One-time"
    
    def test_once_next_due_shows_completed(self, once_chore):
        """One-time chore should show 'Completed' if done"""
        once_chore.completed = True
        assert once_chore.get_next_due_date() == "Completed"


# ============================================================================
# EDGE CASES AND SPECIAL DATES
# ============================================================================

class TestEdgeCases:
    """Test edge cases and special dates"""
    
    def test_monthly_chore_on_31st(self, session):
        """Monthly chore due on 31st should handle months with fewer days"""
        chore = Chore(
            name="31st Chore",
            frequency='monthly',
            frequency_details='31'
        )
        session.add(chore)
        session.commit()
        
        # February doesn't have 31 days
        with freeze_time("2024-02-15"):
            # Should not be due today
            assert chore.is_due_today() is False
    
    def test_leap_year_february_29(self, session):
        """Test handling of February 29 in leap year"""
        chore = Chore(
            name="Leap Day Chore",
            frequency='monthly',
            frequency_details='29'
        )
        session.add(chore)
        session.commit()
        
        with freeze_time("2024-02-29"):  # Leap year
            assert chore.is_due_today() is True
    
    def test_weekly_chore_multiple_same_days_in_details(self, session):
        """Weekly chore should handle day names properly"""
        chore = Chore(
            name="Multiple Days",
            frequency='weekly',
            frequency_details='Monday,Monday,Wednesday'  # Redundant Monday
        )
        session.add(chore)
        session.commit()
        
        with freeze_time("2024-07-29"):  # Monday
            assert chore.is_due_today() is True
    
    def test_monthly_chore_completion_count_persists(self, session):
        """Chore completion count should persist correctly"""
        chore = Chore(
            name="Persistent",
            frequency='daily'
        )
        session.add(chore)
        session.commit()
        
        # Add multiple completions
        for i in range(10, 0, -1):
            with freeze_time(datetime.now() - timedelta(days=i)):
                completion = Completion(chore_id=chore.id, completed_at=datetime.now())
                session.add(completion)
        session.commit()
        
        assert chore.get_completion_count() == 10
    
    def test_empty_frequency_details_handles_gracefully(self, session):
        """Chore with empty frequency_details should handle gracefully"""
        chore = Chore(
            name="Empty Details",
            frequency='weekly',
            frequency_details=None
        )
        session.add(chore)
        session.commit()
        
        # Should not crash
        assert chore.is_due_today() is False