import re
from datetime import datetime, timedelta
from models import Expense, Income, Goal, db

def categorize_expense(description):
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
    # 50/30/20 rule roughly
    return {
        'Needs': total_income * 0.50,
        'Wants': total_income * 0.30,
        'Savings': total_income * 0.20
    }

def get_weekly_insights():
    now = datetime.utcnow()
    one_week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)
    
    current_week_expenses = Expense.query.filter(Expense.date >= one_week_ago).all()
    past_week_expenses = Expense.query.filter(Expense.date >= two_weeks_ago, Expense.date < one_week_ago).all()
    
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
            "text": f"You've tracked your first week of expenses! Total: ₹{current_total}"
        })
        
    if highest_category:
        insights.append({
            "type": "alert",
            "text": f"You're spending the most on {highest_category} (₹{categories[highest_category]}). Keep an eye on it!"
        })
        
    if current_total == 0:
        insights.append({
            "type": "info",
            "text": "You haven't tracked any expenses this week. Adding some now!"
        })
        
    return {
        'current_total': current_total,
        'highest_category': highest_category,
        'insights': insights,
        'category_breakdown': categories
    }
