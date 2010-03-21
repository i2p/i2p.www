from werkzeug import BaseRequest, BaseResponse, ETagResponseMixin, escape, run_simple, SharedDataMiddleware
from werkzeug.exceptions import HTTPException
from werkzeug.routing import RequestRedirect
from jinja import Environment, FileSystemLoader, MemcachedFileSystemLoader
from jinja.exceptions import TemplateNotFound
import os
from time import time
from random import randint

class Request(BaseRequest):
    """Useful subclass of the default request that knows how to build urls."""

    def __init__(self, environ):
        BaseRequest.__init__(self, environ)


class Response(BaseResponse, ETagResponseMixin):
    """Subclass of base response that has a default mimetype of text/html."""
    default_mimetype = 'text/html'


# setup jinja
try:
    env = Environment(loader=MemcachedFileSystemLoader('pages', memcache_host=['127.0.0.1:11211'], memcache_time=600))
except RuntimeError:
    env = Environment(loader=FileSystemLoader('pages', use_memcache=False, auto_reload=True))

def app(environ, start_response):
    """The WSGI application that connects all together."""
    req = Request(environ)
    path = req.path[1:].lower()
    # do theme handling
    theme = 'light'
    if 'style' in req.cookies:
        theme = req.cookies['style']
    if 'theme' in req.args.keys():
        theme = req.args['theme']
    if not os.path.isfile('static/styles/%s.css' % theme):
        theme = 'light'
    if path == '':
        path = 'index'
    mime_type='text/html'
    try:
        try:
            path.index('.')
            if path.split('.')[-1].isdigit() and not path.split('.')[-1].isalpha():
                raise ValueError()
            tmpl = env.get_template(path)
            if path[-3:] == 'txt':
                mime_type='text/plain'
            if path[-3:] == 'xml':
                mime_type='text/xml'
        except ValueError:
            tmpl = env.get_template(path + '.html')
    except TemplateNotFound:
        tmpl = env.get_template('not_found.html')
    resp = Response(tmpl.render(static=False, theme=theme), mimetype=mime_type)
    # more theme handling
    if theme == 'light' and 'style' in req.cookies:
        resp.delete_cookie('style')
    elif theme != 'light':
        resp.set_cookie('style', theme)
    resp.add_etag()
    resp.make_conditional(req)
    return resp(environ, start_response)

app = SharedDataMiddleware(app, {
    '/_static': os.path.join(os.path.dirname(__file__), 'static')
})

if __name__ == '__main__':
    run_simple('localhost', 5009, app)
