import os
import re
import functools
import random
from flask import (
    Flask, render_template, request, jsonify,
    redirect, url_for, session, flash
)
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from models import db, Expense, Income, Goal, User
from logic import (
    categorize_expense, get_budget_prediction,
    get_weekly_insights, get_overview_stats
)
from migrate import run_migrations
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'xray-secret-key-change-in-production')

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'expense.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    run_migrations()


# ─── ID Generation ──────────────────────────────────────────────────────────

def clean_name(name):
    """Strip non-alphanumeric chars and capitalize first letter."""
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', name).strip()
    if not cleaned:
        return 'User'
    return cleaned[0].upper() + cleaned[1:]


def generate_xray_id(name):
    """
    Generate a unique XRay ID from a display name.
    Format: [Name]XRay  →  if taken: [Name]1XRay, [Name]2XRay, ...
    Returns the first available candidate.
    """
    base = clean_name(name)
    # Try base form first
    candidate = f"{base}XRay"
    if not User.query.filter_by(expense_xray_id=candidate).first():
        return candidate
    # Sequential numeric suffix
    for i in range(1, 10000):
        candidate = f"{base}{i}XRay"
        if not User.query.filter_by(expense_xray_id=candidate).first():
            return candidate
    # Final fallback with random large number
    return f"{base}{random.randint(10000, 99999)}XRay"


# ─── Auth Helpers ─────────────────────────────────────────────────────────────

def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def get_current_user():
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])


# ─── Public API ───────────────────────────────────────────────────────────────

@app.route('/api/suggest_id')
def suggest_id():
    """
    Given a name, return a suggested unique Expense X-Ray ID.
    Called live during signup for the ID preview.
    """
    name = request.args.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Name required'}), 400
    suggested = generate_xray_id(name)
    return jsonify({'suggested_id': suggested})


# ─── Public Routes ─────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    error = None
    if request.method == 'POST':
        xray_id = request.form.get('expense_xray_id', '').strip()
        password = request.form.get('password', '')

        # Case-insensitive lookup
        user = User.query.filter(
            db.func.lower(User.expense_xray_id) == xray_id.lower()
        ).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['xray_id'] = user.expense_xray_id
            session['display_name'] = user.name or user.expense_xray_id
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid Expense X-Ray ID or password.'

    return render_template('login.html', error=error)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    error = None
    generated_id = None

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not name:
            error = 'Your name is required.'
        elif not password:
            error = 'Password is required.'
        elif len(password) < 6:
            error = 'Password must be at least 6 characters.'
        elif password != confirm:
            error = 'Passwords do not match.'
        else:
            # Generate ID server-side — handles race conditions via IntegrityError retry
            xray_id = generate_xray_id(name)
            for attempt in range(5):
                try:
                    new_user = User(
                        name=name,
                        expense_xray_id=xray_id,
                        password_hash=generate_password_hash(password),
                        monthly_income=0.0
                    )
                    db.session.add(new_user)
                    db.session.commit()
                    session['user_id'] = new_user.id
                    session['xray_id'] = new_user.expense_xray_id
                    session['display_name'] = new_user.name
                    return redirect(url_for('dashboard'))
                except IntegrityError:
                    db.session.rollback()
                    # ID was taken by a concurrent signup — try next number
                    base = clean_name(name)
                    suffix = random.randint(1, 9999)
                    xray_id = f"{base}{suffix}XRay"
            error = 'Could not create account. Please try again.'

    return render_template('signup.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# ─── Protected Routes ──────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    expenses = Expense.query.filter_by(user_id=user.id).order_by(Expense.date.desc()).limit(15).all()
    insights = get_weekly_insights(user_id=user.id)
    overview = get_overview_stats(user_id=user.id)
    return render_template(
        'dashboard.html',
        expenses=expenses,
        insights=insights,
        overview=overview,
        user=user
    )


@app.route('/api/add_expense', methods=['POST'])
@login_required
def add_expense():
    user = get_current_user()
    data = request.json
    try:
        amount = float(data.get('amount', 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid amount"}), 400

    description = data.get('description', '').strip()
    category = data.get('category', '').strip()

    if not description:
        return jsonify({"error": "Description is required"}), 400
    if not category:
        category = categorize_expense(description)
    if amount <= 0:
        return jsonify({"error": "Amount must be greater than zero"}), 400

    new_expense = Expense(
        amount=amount,
        description=description,
        category=category,
        user_id=user.id
    )
    db.session.add(new_expense)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Expense added successfully!",
        "category": category,
        "id": new_expense.id,
        "amount": amount,
        "description": description,
        "date": new_expense.date.strftime('%d %b %Y')
    })


@app.route('/api/delete_expense/<int:expense_id>', methods=['DELETE'])
@login_required
def delete_expense(expense_id):
    user = get_current_user()
    expense = Expense.query.filter_by(id=expense_id, user_id=user.id).first()
    if not expense:
        return jsonify({"error": "Expense not found or access denied"}), 404
    db.session.delete(expense)
    db.session.commit()
    return jsonify({"success": True})


@app.route('/set-budget', methods=['GET', 'POST'])
@app.route('/set_budget', methods=['GET', 'POST'])
@login_required
def set_budget():
    user = get_current_user()

    if request.method == 'POST':
        try:
            income_amount = float(request.form.get('income_amount', 0))
            if income_amount < 0:
                raise ValueError
            user.monthly_income = income_amount
            db.session.commit()
        except (ValueError, TypeError):
            flash('Invalid income amount.', 'error')

    income = user.monthly_income or 0
    prediction = get_budget_prediction(income) if income > 0 else None

    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    this_month_expenses = Expense.query.filter(
        Expense.user_id == user.id,
        Expense.date >= month_start
    ).all()
    spent_this_month = sum(e.amount for e in this_month_expenses)
    remaining = max(0, income - spent_this_month)
    spent_pct = min(100, (spent_this_month / income * 100) if income > 0 else 0)

    return render_template(
        'set_budget.html',
        income=income,
        prediction=prediction,
        spent_this_month=spent_this_month,
        remaining=remaining,
        spent_pct=spent_pct,
        user=user
    )


@app.route('/savings-goals', methods=['GET', 'POST'])
@app.route('/savings_goals', methods=['GET', 'POST'])
@login_required
def savings_goals():
    user = get_current_user()

    if request.method == 'POST':
        if 'goal_name' in request.form:
            name = request.form.get('goal_name', '').strip()
            try:
                target = float(request.form.get('goal_amount', 0))
            except (ValueError, TypeError):
                flash('Invalid target amount.', 'error')
                target = None

            if name and target and target > 0:
                goal = Goal(
                    name=name,
                    target_amount=target,
                    current_amount=0,
                    user_id=user.id
                )
                db.session.add(goal)
                db.session.commit()

    goals = Goal.query.filter_by(user_id=user.id).all()
    return render_template('savings_goals.html', goals=goals, user=user)


@app.route('/api/update_goal', methods=['POST'])
@login_required
def update_goal():
    user = get_current_user()
    data = request.json
    goal_id = data.get('goal_id')
    amount = data.get('amount')

    goal = Goal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        return jsonify({"error": "Goal not found or access denied"}), 404

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid amount"}), 400

    goal.current_amount += amount
    db.session.commit()
    return jsonify({
        "success": True,
        "current_amount": goal.current_amount,
        "target_amount": goal.target_amount,
        "percent": min(100, (goal.current_amount / goal.target_amount * 100))
    })


@app.route('/api/delete_goal/<int:goal_id>', methods=['DELETE'])
@login_required
def delete_goal(goal_id):
    user = get_current_user()
    goal = Goal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        return jsonify({"error": "Goal not found or access denied"}), 404
    db.session.delete(goal)
    db.session.commit()
    return jsonify({"success": True})


@app.route('/reports')
@login_required
def reports():
    user = get_current_user()
    insights = get_weekly_insights(user_id=user.id)
    return render_template('reports.html', insights=insights, user=user)


@app.route('/profile')
@login_required
def profile():
    user = get_current_user()
    expense_count = Expense.query.filter_by(user_id=user.id).count()
    goal_count = Goal.query.filter_by(user_id=user.id).count()
    return render_template('profile.html', user=user,
                           expense_count=expense_count, goal_count=goal_count)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
