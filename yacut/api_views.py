from http import HTTPStatus

from flask import jsonify, request

from . import app
from .error_handlers import InvalidAPIUsage, ExistenceError, ValidatingError
from .models import URLMap

MISSING_REQUEST_BODY = 'Отсутствует тело запроса'
URL_IS_REQUIRED_FIELD = '"url" является обязательным полем!'
SHORT_ID_NOT_FOUND = 'Указанный id не найден'
SHORT_GENERATOR_ERROR = 'Не удалось сгенерировать короткую ссылку'
NAME_USED = 'Имя "{name}" уже занято.'


@app.route('/api/id/<string:short_id>/')
def get_url(short_id):
    url_map = URLMap.get_urlmap_item(short_id)
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
    custom_id = data.get('custom_id')
    try:
        url_map = URLMap.create_urlmap(
            data.get('url'),
            custom_id,
            validate=True
        )
    except ExistenceError:
        raise InvalidAPIUsage(NAME_USED.format(name=custom_id))
    except ValidatingError as error:
        raise InvalidAPIUsage(error.message)
    return jsonify(url_map.to_dict()), HTTPStatus.CREATED
