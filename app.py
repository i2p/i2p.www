from jinja2 import Environment, FileSystemLoader
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

app=application=Flask(__name__, template_folder=TEMPLATE_DIR)
app.debug=bool(os.environ.get('APP_DEBUG', 'False'))

@app.url_value_preprocessor
def pull_lang(endpoint, values):
    if not values:
        return
    g.lang=values.pop('lang', None)

@app.view('/')
def main_index():
    redirect(url_for('site_show', lang='en'))

@app.view('/<string:lang>/site/')
@app.view('/<string:lang>/site/<path:page>')
def site_show(page=''):
    # TODO: set content_type

@app.view('/<string:lang>/meetings/')
def meetings_index():
    return render_template('meetings/index.html')

@app.view('/<string:lang>/meetings/<int:id>')
def meetings_show(id):
    # TODO: implement

@app.view('/<string:lang>/meetings/<int:id>/raw')
def meetings_show_raw(id):
    # TODO: implement

@app.view('/<string:lang>/download')
def downloads_list():
    # TODO: implement

@app.view('/<string:lang>/download/<path:file>')
def downloads_select(file):
    # TODO: implement

@app.view('/download/<string:protocol>/any/<path:file>')
@app.view('/download/<string:protocol>/<string:mirror>/<path:file>')
def downloads_redirect(protocol, file, mirror=None):
    # TODO: implement

@app.view('/<string:lang>/blog/')
@app.view('/<string:lang>/blog/page/<int:page>')
def blog_index(page=0):
    # TODO: implement

@app.view('/<string:lang>/blog/entry/<path:slug>')
def blog_entry(slug):
    # TODO: implement

@app.view('/feed/blog/rss')
def blog_rss():
    # TODO: implement

@app.view('/feed/blog/atom')
def blog_atom():
    # TODO: implement

@app.view('/<string:f>'):
def legacy_show(f):
    # TODO: redirect to correct new url

@app.view('/meeting<int:id>')
@app.view('/meeting<int:id>.html')
def legacy_meeting(id):
    redirect(url_for('meetings_show', id=id, lang='en'))

@app.view('/status-<int:year>-<int:month>-<int:day>')
@app.view('/status-<int:year>-<int:month>-<int:day>.html')
def legacy_status(year, month, day):
    redirect(url_for('blog_entry', lang='en', slug=('%s/%s/%s/status' % (year, month, day))))
