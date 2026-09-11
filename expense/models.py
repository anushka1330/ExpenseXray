from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)           # Display name (e.g. "Rahul")
    expense_xray_id = db.Column(db.String(100), nullable=False, unique=True)  # e.g. "RahulXRay"
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    monthly_income = db.Column(db.Float, default=0.0)

    expenses = db.relationship('Expense', backref='owner', lazy=True)
    goals = db.relationship('Goal', backref='owner', lazy=True)

class Expense(db.Model):
    __tablename__ = 'expense'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    # user_id is nullable to preserve existing orphan records
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class Income(db.Model):
    __tablename__ = 'income'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Goal(db.Model):
    __tablename__ = 'goal'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0)
    deadline = db.Column(db.DateTime, nullable=True)
    # user_id is nullable to preserve existing orphan records
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
