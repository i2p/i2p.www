from werkzeug import BaseRequest, BaseResponse, run_simple
from werkzeug.exceptions import HTTPException
from werkzeug.routing import RequestRedirect
from random import randint

class Request(BaseRequest):
    """Useful subclass of the default request that knows how to build urls."""

    def __init__(self, environ):
        BaseRequest.__init__(self, environ)


class Response(BaseResponse):
    """Subclass of base response that has a default mimetype of text/html."""
    default_mimetype = 'text/html'

def read_mirrors():
    file = open('mirrors', 'r')
    dat = file.read()
    file.close()
    return dat.split('\n')


def app(environ, start_response):
    """The WSGI application that connects all together."""
    req = Request(environ)
    mirrors = read_mirrors()
    mirror = mirrors[randint(0, len(mirrors) - 1)]
    resp = RequestRedirect(mirror % req.path)
    return resp(environ, start_response)

if __name__ == '__main__':
    run_simple('localhost', 5008, app)
