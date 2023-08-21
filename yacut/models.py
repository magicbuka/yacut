from datetime import datetime
from random import sample
from re import match

from flask import url_for

from settings import (
    GENERATE_SHORT_RETRIES, MAX_URL_LENGTH, PATTERN,
    REDIRECT_VIEW, SHORT_LENGTH, SYMBOLS, USER_SHORT_LENGTH
)
from yacut import db

from .error_handlers import CreatingError, ExistenceError, ValidatingError

WRONG_SHORT_NAME = 'Указано недопустимое имя для короткой ссылки'
WRONG_LENGTH = (
    'Размер ссылки {get_length} '
    f'больше допустимого {MAX_URL_LENGTH}'
)
NAME_USED = 'Имя "{name}" уже занято.'
SHORT_CREATION_ERROR = 'Не удалось сгенерировать короткую ссылку'


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(MAX_URL_LENGTH), nullable=False)
    short = db.Column(db.String(SHORT_LENGTH), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def to_dict(self):
        return dict(
            url=self.original,
            short_link=url_for(
                REDIRECT_VIEW, short=self.short, _external=True
            ),
        )

    @staticmethod
    def create_urlmap(original, custom_id, validate=False):
        if validate:
            if len(original) > MAX_URL_LENGTH:
                raise ValidatingError(WRONG_LENGTH.format(
                    get_length=len(original)
                ))
            if custom_id:
                if len(custom_id) > USER_SHORT_LENGTH:
                    raise ValidatingError(WRONG_SHORT_NAME)
                if not match(PATTERN, custom_id):
                    raise ValidatingError(WRONG_SHORT_NAME)
                if URLMap.get_urlmap_item(custom_id):
                    raise ExistenceError(NAME_USED.format(name=custom_id))
        if not custom_id:
            custom_id = URLMap.create_unique_custom_id()
        entry = URLMap(original=original, short=custom_id)
        db.session.add(entry)
        db.session.commit()
        return entry

    @staticmethod
    def create_unique_custom_id():
        for _ in range(GENERATE_SHORT_RETRIES):
            custom_id = ''.join(sample(SYMBOLS, SHORT_LENGTH))
            if not URLMap.get_urlmap_item(custom_id):
                return custom_id
        raise CreatingError(SHORT_CREATION_ERROR)

    @staticmethod
    def get_urlmap_item(custom_id):
        return URLMap.query.filter_by(short=custom_id).first()

    @staticmethod
    def get_urlmap_or_404(custom_id):
        return URLMap.query.filter_by(short=custom_id).first_or_404().original
