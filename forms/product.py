from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, TextAreaField, FileField
from wtforms.validators import DataRequired


class AddProductForm(FlaskForm):
    cost = FloatField(label='Цена', validators=[DataRequired()])
    title = StringField(label='Заголовок', validators=[DataRequired()])
    content = TextAreaField('Описание', validators=[DataRequired()])
    image = FileField(label='Фотография')
    submit = SubmitField('Сохранить')
