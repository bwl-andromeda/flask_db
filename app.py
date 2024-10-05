from flask import Flask, render_template, redirect, url_for, flash
from config import Config
from extensions import db
from forms import TransactionForm
from datetime import datetime
from flask_migrate import Migrate
app = Flask("FlaskAPP")
app.config.from_object(Config)
migrate=Migrate(app,db)
from models import User, Category, Transaction
db.init_app(app)
with app.app_context():
    db.create_all()
    if Category.query.count() == 0:
        categories = [
            Category(name='Еда'),
            Category(name='Транспорт'),
            Category(name='Прочее'),
            Category(name='Другое')
        ]
        db.session.bulk_save_objects(categories)
        db.session.commit()

@app.route('/')
@app.route('/dashboard')
def dashboard():
    transactions = Transaction.query.all()
    total_income = sum(t.amount for t in transactions if t.type == 'заработок')
    total_expense = sum(t.amount for t in transactions if t.type == 'трата')
    balance = total_income - total_expense
    return render_template('dashboard.html', transactions=transactions, balance=balance, total_income=total_income, total_expense=total_expense)

@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    form = TransactionForm()
    form.category.choices = [(category.id, category.name) for category in Category.query.all()]

    if form.validate_on_submit():
        transaction = Transaction(
            amount=form.amount.data,
            type=form.type.data,
            description=form.description.data,
            category_id=form.category.data,
            user_id=1,  # Replace with current logged in user
            date=datetime.utcnow()
        )
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('new_transaction.html', form=form)

@app.route('/transactions/delete/<int:id>')
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
    db.create_all()

