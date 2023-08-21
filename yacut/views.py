from flask import flash, redirect, render_template, url_for

from settings import REDIRECT_VIEW

from . import app
from .error_handlers import ExistenceError, ValidatingError
from .forms import URLMapForm
from .models import URLMap


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLMapForm()
    if not form.validate_on_submit():
        return render_template('index.html', form=form)
    try:
        return render_template(
            'index.html',
            form=form,
            short_url=url_for(
                REDIRECT_VIEW,
                short=URLMap.create_urlmap(
                    original=form.original_link.data,
                    custom_id=form.custom_id.data,
                    validate=True
                ).short,
                _external=True
            )
        )
    except ExistenceError as error:
        flash(error)
    except ValidatingError as error:
        flash(error)
    return render_template('index.html', form=form)


@app.route('/<string:short>')
def redirect_view(short):
    return redirect(URLMap.get_urlmap_or_404(short))
