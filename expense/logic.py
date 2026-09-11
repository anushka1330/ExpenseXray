import re
from datetime import datetime, timedelta
from models import Expense, Income, Goal, db

def categorize_expense(description):
    """Auto-categorize expense based on description keywords (Indian context)."""
    if not description:
        return 'Other'
        
    description = description.lower()
    
    categories = {
        'Food': ['swiggy', 'zomato', 'food', 'restaurant', 'coffee', 'cafe', 'grocery', 'supermarket', 'burger', 'pizza', 'lunch', 'dinner'],
        'Travel': ['uber', 'ola', 'taxi', 'cab', 'metro', 'train', 'bus', 'flight', 'petrol', 'fuel', 'auto'],
        'Shopping': ['amazon', 'flipkart', 'myntra', 'clothes', 'shoes', 'electronics', 'mall', 'shopping'],
        'Entertainment': ['movie', 'netflix', 'spotify', 'prime', 'cinema', 'games', 'concert'],
        'Bills': ['electricity', 'water', 'internet', 'wifi', 'rent', 'recharge', 'mobile', 'bill'],
        'Health': ['doctor', 'medicine', 'hospital', 'pharmacy', 'clinic', 'gym']
    }
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if re.search(r'\b' + keyword + r'\b', description):
                return category
                
    return 'Other'


def get_budget_prediction(total_income):
    """
    Calculate budget allocation using the 50/30/20 rule.
    Preserved exactly from original logic.
    """
    # 50/30/20 rule roughly
    return {
        'Needs': total_income * 0.50,
        'Wants': total_income * 0.30,
        'Savings': total_income * 0.20
    }


def get_weekly_insights(user_id=None):
    """
    Calculate weekly spending insights for a specific user.
    If user_id is None, calculates across all expenses (legacy behavior).
    Preserved exactly from original logic, with optional user_id filtering added.
    """
    now = datetime.utcnow()
    one_week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)

    # Build queries — filter by user_id if provided
    if user_id is not None:
        current_week_expenses = Expense.query.filter(
            Expense.date >= one_week_ago,
            Expense.user_id == user_id
        ).all()
        past_week_expenses = Expense.query.filter(
            Expense.date >= two_weeks_ago,
            Expense.date < one_week_ago,
            Expense.user_id == user_id
        ).all()
    else:
        current_week_expenses = Expense.query.filter(Expense.date >= one_week_ago).all()
        past_week_expenses = Expense.query.filter(
            Expense.date >= two_weeks_ago, Expense.date < one_week_ago
        ).all()
    
    current_total = sum(e.amount for e in current_week_expenses)
    past_total = sum(e.amount for e in past_week_expenses)
    
    # Categorize current week
    categories = {}
    for e in current_week_expenses:
        categories[e.category] = categories.get(e.category, 0) + e.amount
        
    highest_category = max(categories, key=categories.get) if categories else None
    
    insights = []
    if current_total > past_total and past_total > 0:
        increase = ((current_total - past_total) / past_total) * 100
        insights.append({
            "type": "warning", 
            "text": f"Your spending increased by {increase:.1f}% compared to last week."
        })
    elif past_total > 0 and current_total < past_total:
        decrease = ((past_total - current_total) / past_total) * 100
        insights.append({
            "type": "success",
            "text": f"Great job! You spent {decrease:.1f}% less than last week."
        })
    elif past_total == 0 and current_total > 0:
        insights.append({
            "type": "info",
            "text": f"You've tracked your first week of expenses! Total: ₹{current_total:,.2f}"
        })
        
    if highest_category:
        insights.append({
            "type": "alert",
            "text": f"You're spending the most on {highest_category} (₹{categories[highest_category]:,.2f}). Keep an eye on it!"
        })
        
    if current_total == 0:
        insights.append({
            "type": "info",
            "text": "You haven't tracked any expenses this week. Start adding some now!"
        })
        
    return {
        'current_total': current_total,
        'past_total': past_total,
        'highest_category': highest_category,
        'insights': insights,
        'category_breakdown': categories
    }


def get_overview_stats(user_id):
    """
    Calculate overview statistics for a user's dashboard.
    All values come from the actual database.
    """
    from sqlalchemy import func
    import calendar

    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # All-time totals
    all_expenses = Expense.query.filter_by(user_id=user_id).all()
    total_all_time = sum(e.amount for e in all_expenses)

    # This month's spending
    this_month_expenses = Expense.query.filter(
        Expense.user_id == user_id,
        Expense.date >= month_start
    ).all()
    this_month_total = sum(e.amount for e in this_month_expenses)

    # Category breakdown all-time
    cat_totals = {}
    for e in all_expenses:
        cat_totals[e.category] = cat_totals.get(e.category, 0) + e.amount
    top_category = max(cat_totals, key=cat_totals.get) if cat_totals else None

    # Expense count
    expense_count = len(all_expenses)

    # Largest single expense
    largest_expense = max((e.amount for e in all_expenses), default=0)

    # Goal count
    goal_count = Goal.query.filter_by(user_id=user_id).count()

    return {
        'total_all_time': total_all_time,
        'total_expense': total_all_time,
        'this_month_total': this_month_total,
        'top_category': top_category,
        'expense_count': expense_count,
        'goal_count': goal_count,
        'largest_expense': largest_expense,
        'category_breakdown': cat_totals,
    }
