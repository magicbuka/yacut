from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import (
    URL, DataRequired, Length, Optional, Regexp,
    ValidationError
)

from settings import MAX_URL_LENGTH, PATTERN, SYMBOLS, USER_SHORT_LENGTH

from .models import URLMap

REQUIRED_FIELD = 'Обязательное поле'
INVALID_URL = 'Некорректный URL'
ALLOWED_SYMBOLS = 'Допустимы только цифры и латинские буквы {symbols}'
NAME_USED = 'Имя {name} уже занято!'


class URLMapForm(FlaskForm):
    original_link = URLField(
        'Введите ссылку',
        validators=[
            DataRequired(message=REQUIRED_FIELD),
            Length(max=MAX_URL_LENGTH),
            URL(require_tld=True, message=INVALID_URL)
        ]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Length(max=USER_SHORT_LENGTH),
            Optional(),
            Regexp(
                PATTERN,
                message=ALLOWED_SYMBOLS.format(symbols=SYMBOLS)
            )
        ]
    )
    submit = SubmitField('Создать')

    def validate_custom_id(self, field):
        if field.data and URLMap.get_original(short=field.data):
            raise ValidationError(NAME_USED.format(name=field.data))
