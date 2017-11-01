import os
import json
from time import sleep

from flask import Flask, flash, render_template, request, redirect, url_for

import webserver_get
from wtforms import Form, TextField, validators

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'


class ReusableForm(Form):
    name = TextField('https://www.', validators=[validators.required()])


@app.route("/result", methods=['POST'])
def result():
    urlchecked = request.form['name']

    if request.method == 'POST':
        name = request.form['name']

        name_clean = ''.join([
            c
            for c in '' + name.replace('https://', '').replace('http://', '')
            .replace('www.', '') if c.isalpha()])

        # def run_command():
        #     return webserver_get.GetSite(name, name_clean=name_clean)

        # value = 'fakevalue'

        # print(
        #     value,)

        # if not os.path.exists(value):
        #     try:
        #         result = run_command()
        #         sleep(.5)
        value = 'static/{}.json'.format(name_clean)

        file = json.load(open(value))
        #     finally:
        #         print("what")
        # else:
        #     pass

    return render_template("index.html", urlentered=urlchecked, value=file)


@app.route("/", methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)

    print(form.errors)
    if request.method == 'POST':
        name = request.form['name']
        print(name)

        if form.validate():

            name_clean = ''.join([
                c
                for c in '' + name.replace('https://', '').replace(
                    'http://', '').replace('www.', '') if c.isalpha()])

            def run_command():

                return webserver_get.GetSite(name, name_clean=name_clean)

            value = 'fakevalue'

            print(
                value,)

            if not os.path.exists(value):
                try:
                    result = run_command()
                    sleep(.5)
                    value = 'static/{}.png'.format(name_clean)
                    if isinstance(result, str):
                        flash(result, 'error')
                        value = 'static/oops.gif'
                finally:

                    del form
            else:
                pass
            #return render_template('index.html', value=value)
            return redirect(url_for('result', results_form=value))

            # Save the comment here.

        else:
            flash('All the form fields are required. ')

    return render_template('submit.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
