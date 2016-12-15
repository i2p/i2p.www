# -*- coding: utf-8 -*-
from flask import Flask, request, g, redirect, url_for, abort, render_template, send_from_directory, safe_join
try:
    from flaskext.babel import Babel
except ImportError:
    from flask_babel import Babel
try:
    from flask.ext.cache import Cache
except ImportError:
    from flask_cache import Cache
from docutils.core import publish_parts
import os.path
import os

try:
    from i2p2www import settings
except ImportError:
    settings = None



###########
# Constants

CURRENT_I2P_VERSION = '0.9.28'

CANONICAL_DOMAIN = 'geti2p.net'

CACHE_CONFIG = settings.CACHE_CONFIG if settings and hasattr(settings, 'CACHE_CONFIG') else {
    'CACHE_DEFAULT_TIMEOUT': 600,
    }

BLOG_POSTS_PER_FEED = 10
BLOG_POSTS_PER_PAGE = 10
MEETINGS_PER_PAGE = 20

# This list defines the order that languages appear in the dropdown.
SUPPORTED_LANGS = [
    'en',
    'de',
    'es',
    'fr',
    'ru',
    'zh',
    'ar',
    'id',
    'zh_TW',
    'el',
    'he',
    'it',
    'ja',
    'ko',
    'mg',
    'nl',
    'fa',
    'pl',
    'pt',
    'pt_BR',
    'ro',
    'fi',
    'sv',
    'tr',
    'uk',
    ]

SUPPORTED_LANG_NAMES = {
    'ar': u'Arabic العربية',
    'id': u'Bahasa Indonesia',
    'zh': u'Chinese 中文',
    'zh_TW': u'Chinese 中文 (繁體中文, 台灣)',
    'de': u'Deutsch',
    'en': u'English',
    'es': u'Castellano',
    'fr': u'Français',
    'el': u'Greek Ελληνικά',
    'he': u'Hebrew עברית',
    'it': u'Italiano',
    'ja': u'Japanese 日本語',
    'ko': u'Korean 한국말',
    'mg': u'Fiteny Malagasy',
    'nl': u'Nederlands',
    'fa': u'Persian فارسی',
    'pl': u'Polski',
    'pt': u'Português',
    'pt_BR': u'Português do Brasil',
    'ro': u'Română',
    'ru': u'Russian Русский язык',
    'fi': u'Suomi',
    'sv': u'Svenska',
    'tr': u'Türkçe',
    'uk': u'Ukrainian Українська',
    }

RTL_LANGS = [
    'he',
    'ar',
    ]

DEFAULT_GETTEXT_DOMAIN = 'priority'
GETTEXT_DOMAIN_MAPPING = {
    'about': ['about'],
    'blog': ['blog'],
    'comparison': ['comparison'],
    'docs': ['docs'],
    'get-involved': ['get-involved'],
    'misc': ['misc'],
    'research': ['research'],
    }

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'pages')
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
SPEC_DIR = os.path.join(os.path.dirname(__file__), 'spec')
PROPOSAL_DIR = os.path.join(SPEC_DIR, 'proposals')
BLOG_DIR = os.path.join(os.path.dirname(__file__), 'blog')
MEETINGS_DIR = os.path.join(os.path.dirname(__file__), 'meetings/logs')
SITE_DIR = os.path.join(TEMPLATE_DIR, 'site')
MIRRORS_FILE = os.path.join(TEMPLATE_DIR, 'downloads/mirrors')
ANONBIB_CFG = os.path.join(TEMPLATE_DIR, 'papers/anonbib.cfg')
ANONBIB_FILE = os.path.join(TEMPLATE_DIR, 'papers/anonbib.bib')


###################
# Application setup

class MyFlask(Flask):
    jinja_options = dict(Flask.jinja_options)
    jinja_options.setdefault('extensions',
        []).append('i2p2www.extensions.HighlightExtension')

app = application = MyFlask('i2p2www', template_folder=TEMPLATE_DIR, static_url_path='/_static', static_folder=STATIC_DIR)
app.debug =  bool(os.environ.get('APP_DEBUG', 'False'))
babel = Babel(app, default_domain=DEFAULT_GETTEXT_DOMAIN)
cache = Cache(app, config=CACHE_CONFIG)


#################
# Babel selectors

@babel.localeselector
def get_locale():
    # If viewing specs, require English
    if request.path.startswith('/spec'):
        return 'en'
    # If the language is already set from the url, use that
    if hasattr(g, 'lang'):
        return g.lang
    # otherwise try to guess the language from the user accept
    # header the browser transmits. The best match wins.
    return request.accept_languages.best_match(SUPPORTED_LANGS)

@babel.domainselector
def get_domains():
    domains = []
    frags = request.path.split('/', 2)
    if len(frags) == 3:
        path = frags[2]
        for subpath in GETTEXT_DOMAIN_MAPPING:
            if path.startswith(subpath):
                domains.extend(GETTEXT_DOMAIN_MAPPING[subpath])
    # Always end with the priority domain, as it contains
    # various template strings and is likely to be the most
    # up-to-date (in case of any common translation strings).
    domains.append(DEFAULT_GETTEXT_DOMAIN)
    return domains


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
    if endpoint == 'static' or \
            endpoint.startswith('spec_'):
        # Static urls shouldn't have a lang flag
        # (causes complete reload on lang change)
        # Spec urls shouldn't have a lang flag
        # (adds a spurious ?lang=xx to the url)
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
        # TEMPORARY: enable external themes
        # TODO: Remove this (and the corresponding lines in global/layout.html
        if theme[:7] == 'http://':
            g.exttheme = theme
            theme = 'duck'
    if not os.path.isfile(safe_join(safe_join(STATIC_DIR, 'styles'), '%s/desktop.css' % theme)):
        theme = 'duck'
    g.theme = theme
    @after_this_request
    def remember_theme(resp):
        if g.theme == 'duck' and 'style' in request.cookies:
            resp.delete_cookie('style')
        elif g.theme != 'duck':
            resp.set_cookie('style', g.theme)
        return resp


#######################
# Hooks - after request

@app.after_request
def call_after_request_callbacks(response):
    for callback in getattr(g, 'after_request_callbacks', ()):
        response = callback(response)
    return response


##################
# Template filters

@app.template_filter('restructuredtext')
def restructuredtext(value):
    parts = publish_parts(source=value, writer_name="html")
    return parts['html_body']


################
# Error handlers

@app.errorhandler(404)
def page_not_found(error):
    return render_template('global/error_404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('global/error_500.html'), 500

# Import these to ensure they get loaded
import templatevars
import urls
