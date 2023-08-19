from http import HTTPStatus

from flask import jsonify, request

from . import app
from .error_handlers import InvalidAPIUsage
from .models import URLMap

MISSING_REQUEST_BODY = 'Отсутствует тело запроса'
URL_IS_REQUIRED_FIELD = '"url" является обязательным полем!'
SHORT_ID_NOT_FOUND = 'Указанный id не найден'
SHORT_GENERATOR_ERROR = 'Не удалось сгенерировать короткую ссылку'


@app.route('/api/id/<string:short_id>/')
def get_url(short_id):
    url_map = URLMap.get_original(short=short_id)
    if not url_map:
        raise InvalidAPIUsage(
            SHORT_ID_NOT_FOUND,
            HTTPStatus.NOT_FOUND
        )
    return jsonify({'url': url_map.original})


@app.route('/api/id/', methods=['POST'])
def create_id():
    data = request.get_json(silent=True)
    if not data:
        raise InvalidAPIUsage(MISSING_REQUEST_BODY)
    if 'url' not in data:
        raise InvalidAPIUsage(URL_IS_REQUIRED_FIELD)
    if 'custom_id' not in data or data['custom_id'] is None:
        data['custom_id'] = None
    try:
        return jsonify(
            URLMap.create_short_url(
                original=data.get('url'),
                short=data.get('custom_id')
            ).to_dict()
        ), HTTPStatus.CREATED
    except ValueError as error:
        raise InvalidAPIUsage(f'{error}')
