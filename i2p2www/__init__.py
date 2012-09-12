from jinja2 import Environment, FileSystemLoader, environmentfilter
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, send_from_directory, safe_join
from docutils.core import publish_parts
import os.path
import os
import fileinput
import codecs


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'pages')
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')

BLOG_DIR = os.path.join(os.path.dirname(__file__), 'blog')
MEETINGS_DIR = os.path.join(os.path.dirname(__file__), 'meetings')

app = application = Flask('i2p2www', template_folder=TEMPLATE_DIR, static_url_path='/_static', static_folder=STATIC_DIR)
app.debug =  bool(os.environ.get('APP_DEBUG', 'False'))


##########################
# Hooks - helper functions

def after_this_request(f):
    if not hasattr(g, 'after_request_callbacks'):
        g.after_request_callbacks = []
    g.after_request_callbacks.append(f)
    return f


###########################
# Hooks - url preprocessing

@app.url_value_preprocessor
def pull_lang(endpoint, values):
    if not values:
        return
    g.lang=values.pop('lang', None)

@app.url_defaults
def set_lang(endpoint, values):
    if not values:
        return
    if 'lang' in values:
        return
    if hasattr(g, 'lang'):
        values['lang'] = g.lang


########################
# Hooks - before request

# Detect and store chosen theme
@app.before_request
def detect_theme():
    theme = 'duck'
    if 'style' in request.cookies:
        theme = request.cookies['style']
    if 'theme' in request.args.keys():
        theme = request.args['theme']
    if not os.path.isfile(safe_join('static/styles', '%s.css' % theme)):
        theme = 'duck'
    g.theme = theme
    @after_this_request
    def remember_theme(resp):
        if g.theme == 'duck' and 'style' in request.cookies:
            resp.delete_cookie('style')
        elif g.theme != 'duck':
            resp.set_cookie('style', g.theme)
        return resp


############################
# Hooks - request processing

@app.template_filter('restructuredtext')
def restructuredtext(value):
    parts = publish_parts(source=value, writer_name="html")
    return parts['html_body']


#######################
# Hooks - after request

@app.after_request
def call_after_request_callbacks(response):
    for callback in getattr(g, 'after_request_callbacks', ()):
        response = callback(response)
    return response


###############
# Error handlers

@app.errorhandler(404)
def page_not_found(error):
    return render_template('global/error_404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('global/error_500.html'), 500


#######################
# General page handlers

# Index - redirects to en homepage
@app.route('/')
def main_index():
    return redirect(url_for('site_show', lang='en'))

# Site pages
@app.route('/<string:lang>/site/')
@app.route('/<string:lang>/site/<path:page>')
def site_show(page='index'):
    if page.endswith('.html'):
        return redirect(url_for('site_show', page=page[:-5]))
    name = 'site/%s.html' % page
    page_file = safe_join(TEMPLATE_DIR, name)

    if not os.path.exists(page_file):
        # Could be a directory, so try index.html
        name = 'site/%s/index.html' % page
        page_file = safe_join(TEMPLATE_DIR, name)
        if not os.path.exists(page_file):
            # bah! those damn users all the time!
            abort(404)

    # hah!
    return render_template(name, page=page)


##################
# Meeting handlers

# Meeting index
@app.route('/<string:lang>/meetings/')
def meetings_index():
    return render_template('meetings/index.html')

# Renderer for specific meetings
@app.route('/<string:lang>/meetings/<int:id>')
def meetings_show(id, log=False, rst=False):
    """
    Render the meeting X.
    Either display the raw IRC .log or render as html and include .rst as header if it exists
    """
    # generate file name for the raw meeting file(and header)
    lname = str(id) + '.log'
    hname = str(id) + '.rst'
    lfile = safe_join(MEETINGS_DIR, lname)
    hfile = safe_join(MEETINGS_DIR, hname)

    # check if meeting file exists and throw error if it does not..
    if not os.path.exists(lfile):
        abort(404)

    # if the user just wanted the .log
    if log:
        # hmm... maybe replace with something non-render_template like?
        #        return render_template('meetings/show_raw.html', log=log)
        return send_from_directory(MEETINGS_DIR, lname, mimetype='text/plain')

    log=''
    header=None

    # try to load header if that makes sense
    if os.path.exists(hfile):
        # if the user just wanted the .rst...
        if rst:
            return send_from_directory(MEETINGS_DIR, hname, mimetype='text/plain')

        # open the file as utf-8 file
        with codecs.open(hfile, encoding='utf-8') as fd:
            header = fd.read()
    elif rst:
        abort(404)

    # load log
    with codecs.open(lfile, encoding='utf-8') as fd:
        log = fd.read()

    return render_template('meetings/show.html', log=log, header=header, id=id)

# Just return the raw .log for the meeting
@app.route('/<string:lang>/meetings/<int:id>.log')
def meetings_show_log(id):
    return meetings_show(id, log=True)

# Just return the raw .rst for the meeting
@app.route('/<string:lang>/meetings/<int:id>.rst')
def meetings_show_rst(id):
    return meetings_show(id, rst=True)


###################
# Download handlers

# List of downloads
@app.route('/<string:lang>/download')
def downloads_list():
    # TODO: read mirror list or list of available files
    return render_template('downloads/list.html')

# Specific file downloader
@app.route('/<string:lang>/download/<path:file>')
def downloads_select(file):
    # TODO: implement
    pass

@app.route('/download/<string:protocol>/any/<path:file>')
@app.route('/download/<string:protocol>/<string:mirror>/<path:file>')
def downloads_redirect(protocol, file, mirror=None):
    # TODO: implement
    pass


#####################
# Blog helper methods

def get_blog_index():
    """
    Returns list of valid slugs sorted by date
    """
    # list of slugs
    entries=[]
    # walk over all directories/files
    for v in os.walk(BLOG_DIR):
        # iterate over all files
        slugbase = os.path.relpath(v[0], BLOG_DIR)
        for f in v[2]:
            # ignore all non-.rst files
            if not f.endswith('.rst'):
                continue
            entries.append(safe_join(slugbase, f[:-4]))
    entries.sort()
    return entries

def get_date_from_slug(slug):
    parts = slug.split('/')
    return "%s-%s-%s" % (parts[0], parts[1], parts[2])

def render_blog_entry(slug):
    """
    Render the blog entry
    TODO:
    - caching
    - move to own file
    """
    # check if that file actually exists
    path = safe_join(BLOG_DIR, slug + ".rst")
    if not os.path.exists(path):
        abort(404)

    # read file
    with codecs.open(path, encoding='utf-8') as fd:
        content = fd.read()

    return publish_parts(source=content, source_path=BLOG_DIR, writer_name="html")


###############
# Blog handlers

@app.route('/<string:lang>/blog/')
@app.route('/<string:lang>/blog/page/<int:page>')
def blog_index(page=0):
    slugs = get_blog_index()
    entries= []
    for slug in slugs:
        date = get_date_from_slug(slug)
        title = slug.rsplit('/', 1)[1]
        entries.append((slug, date, title))

    return render_template('blog/index.html', entries=entries)

@app.route('/<string:lang>/blog/entry/<path:slug>')
def blog_entry(slug):
    # try to render that blog entry.. throws 404 if it does not exist
    parts = render_blog_entry(slug)

    if parts:
        # now just pass to simple template file and we are done
        return render_template('blog/entry.html', parts=parts, title=parts['title'], body=parts['fragment'])
    else:
        abort(404)


@app.route('/feed/blog/rss')
def blog_rss():
    # TODO: implement
    pass

@app.route('/feed/blog/atom')
def blog_atom():
    # TODO: implement
    pass


##############
# Legacy paths

@app.route('/meeting<int:id>')
@app.route('/meeting<int:id>.html')
def legacy_meeting(id):
    return redirect(url_for('meetings_show', id=id, lang='en'))

@app.route('/status-<int:year>-<int:month>-<int:day>')
@app.route('/status-<int:year>-<int:month>-<int:day>.html')
def legacy_status(year, month, day):
    return redirect(url_for('blog_entry', lang='en', slug=('%s/%s/%s/status' % (year, month, day))))

LEGACY_MAP={
    'download': 'downloads_list'
}

@app.route('/<string:f>_<string:lang>')
@app.route('/<string:f>_<string:lang>.html')
@app.route('/<string:f>')
@app.route('/<string:f>.html')
def legacy_show(f):
    lang = 'en'
    if hasattr(g, 'lang') and g.lang:
        lang = g.lang
    if f in LEGACY_MAP:
        return redirect(url_for(LEGACY_MAP[f], lang=lang))
    else:
        return redirect(url_for('site_show', lang=lang, page=f))



if __name__ == '__main__':
    app.run(debug=True)
