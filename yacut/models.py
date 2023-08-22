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
WRONG_SHORT = 'Указано недопустимое имя для короткой ссылки'
WRONG_LENGTH = (
    'Размер ссылки {length} '
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
                REDIRECT_VIEW, custom_id=self.short, _external=True
            ),
        )

    @staticmethod
    def create(original, short, validate=False):
        if validate:
            if len(original) > MAX_URL_LENGTH:
                raise ValidatingError(WRONG_LENGTH.format(
                    length=len(original)
                ))
            if short:
                if len(short) > USER_SHORT_LENGTH:
                    raise ValidatingError(WRONG_SHORT_NAME)
                if not match(PATTERN, short):
                    raise ValidatingError(WRONG_SHORT)
                if URLMap.get(short):
                    raise ExistenceError(NAME_USED.format(name=short))
        if not short:
            short = URLMap.create_unique_short_id()
        entry = URLMap(original=original, short=short)
        db.session.add(entry)
        db.session.commit()
        return entry

    @staticmethod
    def create_unique_short_id():
        for _ in range(GENERATE_SHORT_RETRIES):
            short_id = ''.join(sample(SYMBOLS, SHORT_LENGTH))
            if not URLMap.get(short_id):
                return short_id
        raise CreatingError(SHORT_CREATION_ERROR)

    @staticmethod
    def get(short):
        return URLMap.query.filter_by(short=short).first()

    @staticmethod
    def get_or_404(short):
        return URLMap.query.filter_by(short=short).first_or_404()
