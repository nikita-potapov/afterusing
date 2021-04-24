from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, TextAreaField, FileField, BooleanField
from wtforms.validators import DataRequired


class AddProductForm(FlaskForm):
    cost = IntegerField(label='Цена', validators=[DataRequired()])
    title = StringField(label='Заголовок', validators=[DataRequired()])
    content = TextAreaField('Описание', validators=[DataRequired()])
    contact_number = StringField('Контактный телефон', validators=[DataRequired()])
    image = FileField(label='Фотография')
    is_showing_by_user = BooleanField(label='Видно всем')
    is_showing_by_admin = BooleanField(label='Допущено админом')
    submit = SubmitField('Сохранить')
