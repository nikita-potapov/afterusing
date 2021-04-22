from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, TextAreaField, FileField
from wtforms.validators import DataRequired


class AddProductForm(FlaskForm):
    cost = IntegerField(label='Цена', validators=[DataRequired()])
    title = StringField(label='Заголовок', validators=[DataRequired()])
    content = TextAreaField('Описание', validators=[DataRequired()])
    contact_number = StringField('Контактный телефон', validators=[DataRequired()])
    image = FileField(label='Фотография')
    submit = SubmitField('Сохранить')
