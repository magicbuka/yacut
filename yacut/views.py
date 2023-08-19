from flask import flash, redirect, render_template, url_for

from settings import REDIRECT_VIEW

from . import app
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
                short=URLMap.create_short_url(
                    original=form.original_link.data,
                    short=form.custom_id.data,
                    validate=True
                ).short,
                _external=True
            )
        )
    except Exception as error:
        flash(error)
        return render_template('index.html', form=form)


@app.route('/<string:short>')
def redirect_view(short):
    return redirect(URLMap.get_original_or_404(short))
