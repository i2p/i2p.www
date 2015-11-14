# -*- coding: utf8 -*-

import os
import sys
from jinja2 import nodes
from jinja2.ext import Extension, Markup

from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

try:
    import ctags
except ImportError:
    ctags = None

from flask import g

from i2p2www.formatters import I2PHtmlFormatter, TextSpecFormatter
from i2p2www.lexers import DataSpecLexer


# https://stackoverflow.com/questions/2632199/how-do-i-get-the-path-of-the-current-executed-file-in-python?lq=1
def we_are_frozen():
    # All of the modules are built-in to the interpreter, e.g., by py2exe
    return hasattr(sys, "frozen")

def module_path():
    encoding = sys.getfilesystemencoding()
    if we_are_frozen():
        return os.path.dirname(unicode(sys.executable, encoding))
    return os.path.dirname(unicode(__file__, encoding))


class HighlightExtension(Extension):
    """Highlight code blocks using Pygments

    Example::

        {% highlight 'python' %}

        from fridge import Beer

        pint_glass = Beer()
        pint_glass.drink()

        {% endhighlight %}
    """
    tags = set(['highlight'])

    def parse(self, parser):
        lineno = parser.stream.next().lineno

        # extract the language if available
        # Any additional parameters are passed to HtmlFormatter
        lang = None
        formatter = None
        parameters = []
        while parser.stream.current.type != 'block_end':
            if lang or parameters:
                parser.stream.expect('comma')

            name = parser.stream.expect('name')
            if name.value in parameters or (name.value == 'lang' and lang) or (name.value == 'formatter' and formatter):
                parser.fail('parameter %r defined twice.' %
                            name.value, name.lineno,
                            exc=TemplateAssertionError)

            if parser.stream.current.type == 'assign':
                next(parser.stream)
                if name.value == 'lang':
                    lang = parser.parse_expression()
                elif name.value == 'formatter':
                    formatter = parser.parse_expression()
                else:
                    parameters.append(nodes.Pair(nodes.Const(name.value), parser.parse_expression()))

        if lang == None:
            lang = nodes.Const(None)
        if formatter == None:
            formatter = nodes.Const('html')
        parameters = nodes.Dict(parameters)

        # body of the block
        body = parser.parse_statements(['name:endhighlight'], drop_needle=True)

        return nodes.CallBlock(self.call_method('_highlight', [lang, formatter, parameters]),
                               [], [], body).set_lineno(lineno)

    def _highlight(self, lang, formatter, parameters, caller=None):
        # highlight code using Pygments
        body = caller()
        try:
            if lang is None:
                lexer = guess_lexer(body)
            else:
                lexer = get_lexer_by_name(lang, stripall=False)
        except ClassNotFound as e:
            if lang == 'dataspec':
                lexer = DataSpecLexer(stripall=False)
            else:
                print(e)
                sys.exit(1)

        if ctags:
            if 'tagsfile' not in parameters:
                parameters['tagsfile'] = module_path() + '/spec/spectags'

            if 'tagurlformat' not in parameters:
                lang = 'en'
                if hasattr(g, 'lang') and g.lang:
                    lang = g.lang
                parameters['tagurlformat'] = '/spec/%(path)s%(fname)s'

        if formatter == 'textspec':
            formatter = TextSpecFormatter(**parameters)
        else:
            formatter = I2PHtmlFormatter(**parameters)
        code = highlight(Markup(body).unescape(), lexer, formatter)
        return code
