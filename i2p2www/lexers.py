from pygments.lexer import RegexLexer, bygroups
from pygments.token import *

class DataSpecLexer(RegexLexer):
    name = 'DataSpec'
    aliases = ['dataspec']
    filenames = []

    tokens = {
        'root': [
            (r'(\s*)(\+-)', bygroups(Text, Text), 'boundary'),
            (r'(\s+)([\+|])', bygroups(Text, Text), 'content'),
            (r'~', Generic.Strong, 'content'),
            (r'(\s*)([\w=;]+)(\s)(::)(\s)', bygroups(Text, Name.Tag, Text, Operator, Text), 'definition'),
        ],
        'boundary': [
            (r'---\+$', Text, '#pop'),
            (r'(//)(-\+)?$', bygroups(Generic.Strong, Text), '#pop'),
            (r'---\+-', Text),
            (r'---\+\s', Text, '#pop', 'content'),
            (r'(//)(-\+-)', bygroups(Generic.Strong, Text)),
        ],
        'content': [
            (r'(\s*)([\+|])$', bygroups(Text, Text), '#pop'),
            (r'(\s*)(\.\.\.)$', bygroups(Text, Generic.Strong), '#pop'),
            (r'(\s*)(~)$', bygroups(Text, Generic.Strong), '#pop'),
            (r'(\s*)([\w=;]+)$', bygroups(Text, Name.Tag), '#pop'),
            (r'(\s*)([\w=;]+)', bygroups(Text, Name.Tag)),
            (r'(\s*)(\|)', bygroups(Text, Text)),
            (r'(\s*)(\()', bygroups(Text, Punctuation), 'expression'),
        ],
        'expression': [
            (r'(\s*)(\))', bygroups(Text, Punctuation), '#pop'),
            (r'(\s*)(\+)', bygroups(Text, Punctuation)),
            (r'(\s*)(\w+)', bygroups(Text, Name)),
        ],
        'definition': [
            (r'(\s*)([\w=;]+)(\s)(::)(\s)', bygroups(Text, Name.Tag, Text, Operator, Text)),
            (r'(\s*)((?:[A-Z][a-z]+)+)', bygroups(Text, Name.Class)),
            (r'(\s*)([\[\]])', bygroups(Text, Punctuation)),
            (r'(\s*)(\$\w+)', bygroups(Text, Name.Tag)),
            (r'(\s*)([0-9]+)(\+)?', bygroups(Text, Number, Punctuation)),
            (r'(-)([0-9]+)', bygroups(Punctuation, Number)),
            (r'(\s*)(->|<=|>=|\*)', bygroups(Text, Operator)),
            (r'(\s*)([\w()-=\'<>]+)', bygroups(Text, Comment)),
        ],
    }
