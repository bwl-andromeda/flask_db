from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from app import db
from app.models import User, Transaction
from werkzeug.urls import url_parse

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expense = sum(t.amount for t in transactions if t.type == 'expense')
    total_balance = total_income - total_expense
    return render_template('index.html', transactions=transactions,
                           total_income=total_income, total_expense=total_expense,
                           total_balance=total_balance)

@bp.route('/add_transaction', methods=['POST'])
@login_required
def add_transaction():
    amount = float(request.form['amount'])
    type = request.form['type']
    description = request.form['description']
    transaction = Transaction(amount=amount, type=type, description=description, user_id=current_user.id)
    db.session.add(transaction)
    db.session.commit()
    return redirect(url_for('main.index'))

@bp.route('/edit_transaction/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    if transaction.user_id != current_user.id:
        flash('You do not have permission to edit this transaction.')
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        transaction.amount = float(request.form['amount'])
        transaction.type = request.form['type']
        transaction.description = request.form['description']
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('edit_transaction.html', transaction=transaction)

@bp.route('/delete_transaction/<int:id>')
@login_required
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    if transaction.user_id != current_user.id:
        flash('You do not have permission to delete this transaction.')
        return redirect(url_for('main.index'))
    db.session.delete(transaction)
    db.session.commit()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('main.register'))
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('main.index')
            return redirect(next_page)
        flash('Invalid username or password.')
    return render_template('login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))