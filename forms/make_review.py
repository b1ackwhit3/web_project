from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class ReviewForm(FlaskForm):
    place_name = StringField('Место', validators=[DataRequired()])
    mark = SelectField('Оценка', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    opinion = StringField('Скажите пару слов об это месте', validators=[DataRequired()])
    submit = SubmitField('Добавить отзыв')