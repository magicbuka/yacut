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
ALLOWED_SYMBOLS = f'Допустимы только цифры и латинские буквы {SYMBOLS}'
NAME_USED = 'Имя {name} уже занято!'
ENTER_URL = 'Введите ссылку'
ENTER_SHORT_URL = 'Ваш вариант короткой ссылки'
CREATE = 'Создать'


class URLMapForm(FlaskForm):
    original_link = URLField(
        ENTER_URL,
        validators=[
            DataRequired(message=REQUIRED_FIELD),
            Length(max=MAX_URL_LENGTH),
            URL(require_tld=True, message=INVALID_URL)
        ]
    )
    custom_id = StringField(
        ENTER_SHORT_URL,
        validators=[
            Length(max=USER_SHORT_LENGTH),
            Optional(),
            Regexp(
                PATTERN,
                message=ALLOWED_SYMBOLS
            )
        ]
    )
    submit = SubmitField(CREATE)

    def validate_custom_id(self, field):
        if field.data and URLMap.get_urlmap_item(custom_id=field.data):
            raise ValidationError(NAME_USED.format(name=field.data))
