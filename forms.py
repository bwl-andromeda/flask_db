from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class TransactionForm(FlaskForm):
    amount = FloatField('Суммa', validators=[DataRequired()])
    type = SelectField('Тип', choices=[('заработок', 'Заработок'), ('трата', 'Трата')], validators=[DataRequired()])
    description = StringField('Описание', validators=[Length(max=200)])
    category = SelectField('Категория', validators=[DataRequired()])
    submit = SubmitField('Добавить транзакцию')

