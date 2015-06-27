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
            (r'(\s*)(~)', bygroups(Text, Generic.Strong), 'content'),
            (r'(\s*)([\w=;]+)(\s[\w=;]+)*(\s)(::)(\s)', bygroups(Text, Name.Tag, Name.Tag, Text, Operator, Text)),
            (r'(\s*)`((?:[A-Z][a-z0-9]+)(?:[A-Z][a-z0-9]*)*)`', bygroups(Text, Name.Class)),
            (r'(\s*)([A-Z]{2,})', bygroups(Text, Name.Constant)),
            (r'(\s*)([\[\]])', bygroups(Text, Punctuation)),
            (r'(\s*)(\$\w+)', bygroups(Text, Name.Tag)),
            (r'(\s*)([0-9]+)(\+)?', bygroups(Text, Number, Punctuation)),
            (r'(-)([0-9]+)', bygroups(Punctuation, Number)),
            (r'(\s*)(->|<=|>=|\*)', bygroups(Text, Operator)),
            (r'(\s*)([\w()-=\'<>]+)', bygroups(Text, Comment)),
        ],
        'boundary': [
            (r'-{3,}\+$', Text, '#pop'),
            (r'(-*)(//)(-+\+)?$', bygroups(Text, Generic.Strong, Text), '#pop'),
            (r'-{3,}\+-', Text),
            (r'-{3,}\+\s', Text, '#pop', 'content'),
            (r'(-*)(//)(-+\+-)', bygroups(Text, Generic.Strong, Text)),
        ],
        'content': [
            (r'(\s*)(\+-)', bygroups(Text, Text), '#pop', 'boundary'),
            (r'(\s*)([\+|])$', bygroups(Text, Text), '#pop'),
            (r'(\s*)(\.)(\s*)(\.)(\s*)(\.)(\s)', bygroups(Text, Generic.Strong, Text, Generic.Strong, Text, Generic.Strong, Text)),
            (r'(\s*)(\.\.\.)$', bygroups(Text, Generic.Strong), '#pop'),
            (r'(\s*)(~)$', bygroups(Text, Generic.Strong), '#pop'),
            (r'(\s*)([\w=;]+)$', bygroups(Text, Name.Tag), '#pop'),
            (r'(\s*)([\w=;]+)', bygroups(Text, Name.Tag)),
            (r'(\s*)(\|)', bygroups(Text, Text)),
            (r'(\s*)(\()', bygroups(Text, Punctuation), 'expression'),
            (r'(\s*)([+-])', bygroups(Text, Operator)),
        ],
        'expression': [
            (r'(\s*)(\))', bygroups(Text, Punctuation), '#pop'),
            (r'(\s*)([+-])', bygroups(Text, Operator)),
            (r'(\s*)(\$\w+)', bygroups(Text, Name.Tag)),
            (r'(\s*)(\w+)', bygroups(Text, Name)),
        ],
    }
