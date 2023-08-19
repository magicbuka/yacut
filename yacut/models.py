from datetime import datetime
from random import sample
from re import match

from flask import url_for

from settings import (
    GENERATE_SHORT_RETRIES, MAX_URL_LENGTH, PATTERN,
    REDIRECT_VIEW, SHORT_LENGTH, SYMBOLS, USER_SHORT_LENGTH
)
from yacut import db

WRONG_SHORT_NAME = 'Указано недопустимое имя для короткой ссылки'
WRONG_LENGTH = (
    'Размер ссылки {get_length} '
    'больше допустимого {max_length}'
)
NAME_USED = 'Имя "{name}" уже занято.'
SHORT_GENERATOR_ERROR = 'Не удалось сгенерировать короткую ссылку'


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
    def create_short_url(original, short, validate=False):
        if not validate:
            if len(original) > MAX_URL_LENGTH:
                raise ValueError(WRONG_LENGTH.format(
                    get_length=len(original),
                    max_length=MAX_URL_LENGTH
                ))
            if short:
                if len(short) > USER_SHORT_LENGTH:
                    raise ValueError(WRONG_SHORT_NAME)
                if not match(PATTERN, short):
                    raise ValueError(WRONG_SHORT_NAME)
                if URLMap.get_original(short=short):
                    raise ValueError(NAME_USED.format(name=short))
        if not short:
            short = URLMap.get_unique_short_id()
        entry = URLMap(original=original, short=short)
        db.session.add(entry)
        db.session.commit()
        return entry

    @staticmethod
    def get_unique_short_id():
        for _ in range(GENERATE_SHORT_RETRIES):
            short = ''.join(sample(SYMBOLS, SHORT_LENGTH))
            if not URLMap.get_original(short=short):
                return short
        raise ValueError(SHORT_GENERATOR_ERROR)

    @staticmethod
    def get_original(short):
        return URLMap.query.filter_by(short=short).first()

    @staticmethod
    def get_original_or_404(short):
        return URLMap.query.filter_by(short=short).first_or_404().original
