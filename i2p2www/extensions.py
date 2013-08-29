# -*- coding: utf8 -*-

import sys
from jinja2 import nodes
from jinja2.ext import Extension, Markup

from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

from i2p2www.lexers import DataSpecLexer

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
        parameters = []
        while parser.stream.current.type != 'block_end':
            if lang or parameters:
                parser.stream.expect('comma')

            name = parser.stream.expect('name')
            if name.value in parameters or (name.value == 'lang' and lang):
                parser.fail('parameter %r defined twice.' %
                            name.value, name.lineno,
                            exc=TemplateAssertionError)

            if parser.stream.current.type == 'assign':
                next(parser.stream)
                if name.value == 'lang':
                    lang = parser.parse_expression()
                else:
                    parameters.append(nodes.Pair(nodes.Const(name.value), parser.parse_expression()))

        if lang == None:
            lang = nodes.Const(None)
        parameters = nodes.Dict(parameters)

        # body of the block
        body = parser.parse_statements(['name:endhighlight'], drop_needle=True)

        return nodes.CallBlock(self.call_method('_highlight', [lang, parameters]),
                               [], [], body).set_lineno(lineno)

    def _highlight(self, lang, parameters, caller=None):
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

        formatter = HtmlFormatter(**parameters)
        code = highlight(Markup(body).unescape(), lexer, formatter)
        return code

