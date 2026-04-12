import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from models import db, Expense, Income, Goal
from logic import categorize_expense, get_budget_prediction, get_weekly_insights
from datetime import datetime

app = Flask(__name__)
# Absolute path so sqlite db is created correctly in current dir
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'expense.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def dashboard():
    expenses = Expense.query.order_by(Expense.date.desc()).limit(15).all()
    insights = get_weekly_insights()
    return render_template('dashboard.html', expenses=expenses, insights=insights)

@app.route('/api/add_expense', methods=['POST'])
def add_expense():
    data = request.json
    try:
        amount = float(data.get('amount', 0))
    except ValueError:
        return jsonify({"error": "Invalid amount"}), 400
        
    description = data.get('description', '')
    category = data.get('category')
    
    if not category:
        category = categorize_expense(description)
        
    if amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400
        
    new_expense = Expense(amount=amount, description=description, category=category)
    db.session.add(new_expense)
    db.session.commit()
    
    return jsonify({"success": True, "message": "Expense added successfully!", "category": category})

@app.route('/set-budget', methods=['GET', 'POST'])
def set_budget():
    if request.method == 'POST':
        if 'income_amount' in request.form:
            app.config['MONTHLY_INCOME'] = float(request.form['income_amount'])
            
    income = app.config.get('MONTHLY_INCOME', 0)
    prediction = get_budget_prediction(income) if income > 0 else None
    
    return render_template('set_budget.html', income=income, prediction=prediction)

@app.route('/savings-goals', methods=['GET', 'POST'])
def savings_goals():
    if request.method == 'POST':
        if 'goal_name' in request.form:
            name = request.form['goal_name']
            target = float(request.form['goal_amount'])
            goal = Goal(name=name, target_amount=target, current_amount=0)
            db.session.add(goal)
            db.session.commit()
            
    goals = Goal.query.all()
    return render_template('savings_goals.html', goals=goals)

@app.route('/api/update_goal', methods=['POST'])
def update_goal():
    data = request.json
    goal = Goal.query.get(data['goal_id'])
    if goal:
        goal.current_amount += float(data['amount'])
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Goal not found"}), 404

@app.route('/reports')
def reports():
    insights = get_weekly_insights()
    return render_template('reports.html', insights=insights)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
