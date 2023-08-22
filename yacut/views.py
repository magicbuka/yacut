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
                custom_id=URLMap.create(
                    form.original_link.data,
                    form.custom_id.data,
                    True
                ).short,
                _external=True
            )
        )
    except ExistenceError as error:
        flash(error)
    except ValidatingError as error:
        flash(error)
    return render_template('index.html', form=form)


@app.route('/<string:custom_id>')
def redirect_view(custom_id):
    return redirect(URLMap.get_first_or_404(custom_id).original)
