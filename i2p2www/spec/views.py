import codecs
from collections import defaultdict
from docutils import io
from docutils.core import (
    Publisher,
    publish_doctree,
    publish_from_doctree,
    publish_parts,
)
from docutils.readers.doctree import Reader
from flask import (
    abort,
    g,
    make_response,
    redirect,
    render_template,
    render_template_string,
    request,
    safe_join,
    url_for,
)
import os.path

from i2p2www import PROPOSAL_DIR, SPEC_DIR
from i2p2www import helpers


SPEC_METATAGS = {
    'accuratefor': None,
    'category': '',
    'lastupdated': None,
    }
SPEC_LIST_METATAGS = [
    ]
SPEC_CATEGORY_SORT = defaultdict(lambda: 999, {
    'Design': 1,
    'Transports': 2,
    'Protocols': 3,
    })

PROPOSAL_METATAGS = {
    'author': u'I2P devs',
    'created': None,
    'editor': None,
    'implementedin': None,
    'lastupdated': None,
    'status': u'Draft',
    'supercededby': None,
    'supercedes': None,
    'target': None,
    'thread': None,
    }
PROPOSAL_LIST_METATAGS = [
    'supercedes',
    ]
PROPOSAL_STATUS_SORT = defaultdict(lambda: 999, {
    'Open': 1,
    'Accepted': 2,
    'Finished': 3,
    'Closed': 90,
    'Rejected': 100,
    'Draft': 10,
    'Needs-Revision': 11,
    'Dead': 20,
    'Needs-Research': 15,
    'Meta': 0,
    'Reserve': 50,
    'Informational': 80,
    })

METATAG_LABELS = {
    'accuratefor': u'Accurate for',
    'author': u'Author',
    'category': u'Category',
    'created': u'Created',
    'editor': u'Editor',
    'implementedin': u'Implemented in',
    'lastupdated': u'Last updated',
    'status': u'Status',
    'supercededby': u'Superceded by',
    'supercedes': u'Supercedes',
    'target': u'Target',
    'thread': u'Thread',
    }


def get_rsts(directory, meta_parser):
    rsts = []
    for f in os.listdir(directory):
        if f.endswith('.rst'):
            path = safe_join(directory, f)
            # read file header
            header = ''
            with codecs.open(path, encoding='utf-8') as fd:
                for line in fd:
                    header += line
                    if not line.strip():
                        break
            parts = publish_parts(source=header, source_path=directory, writer_name="html")
            meta = meta_parser(parts['meta'])

            rst = {
                'name': f[:-4],
                'title': parts['title'],
            }
            rst.update(meta)
            rsts.append(rst)
    return rsts

def spec_index():
    specs = get_rsts(SPEC_DIR, spec_meta)
    specs.sort(key=lambda s: (SPEC_CATEGORY_SORT[s['category']], s['title']))
    return render_template('spec/index.html', specs=specs)

def proposal_index():
    proposals = get_rsts(PROPOSAL_DIR, proposal_meta)
    for i in range(0, len(proposals)):
        proposals[i]['num'] = int(proposals[i]['name'][:3])
    proposals.sort(key=lambda s: (PROPOSAL_STATUS_SORT[s['status']], s['num']))
    return render_template('spec/proposal-index.html', proposals=proposals)

def proposal_number(number):
    proposals = get_rsts(PROPOSAL_DIR, proposal_meta)
    for proposal in proposals:
        if int(proposal['name'][:3]) == number:
            return proposal_show(proposal['name'])
    else:
        abort(404)

def render_rst(directory, name, meta_parser, template):
    # check if that file actually exists
    path = safe_join(directory, name + '.rst')
    if not os.path.exists(path):
        abort(404)

    # read file
    with codecs.open(path, encoding='utf-8') as fd:
        content = fd.read()

    if not template:
        # Strip out RST
        content = content.replace('.. meta::\n', '')
        content = content.replace('.. contents::\n\n', '')
        content = content.replace('.. raw:: html\n\n', '')
        content = content.replace('\n.. [', '\n[')
        content = content.replace(']_.', '].')
        content = content.replace(']_,', '],')
        content = content.replace(']_', '] ')
        # Change highlight formatter
        content = content.replace('{% highlight', "{% highlight formatter='textspec'")
        # Metatags
        for (metatag, label) in METATAG_LABELS.items():
            content = content.replace('    :%s' % metatag, label)

    # render the post with Jinja2 to handle URLs etc.
    rendered_content = render_template_string(content)
    rendered_content = rendered_content.replace('</pre></div>', '  </pre></div>')

    if not template:
        # Send response
        r = make_response(rendered_content)
        r.mimetype = 'text/plain'
        return r

    # Render the ToC
    doctree = publish_doctree(source=rendered_content)
    bullet_list = doctree[1][1]
    doctree.clear()
    doctree.append(bullet_list)
    reader = Reader(parser_name='null')
    pub = Publisher(reader, None, None,
                    source=io.DocTreeInput(doctree),
                    destination_class=io.StringOutput)
    pub.set_writer('html')
    pub.publish()
    toc = pub.writer.parts['fragment']

    # Remove the ToC from the main document
    rendered_content = rendered_content.replace('.. contents::\n', '')

    # publish the spec with docutils
    parts = publish_parts(source=rendered_content, source_path=directory, writer_name="html")
    meta = meta_parser(parts['meta'])

    if (directory == PROPOSAL_DIR):
        meta['num'] = int(name[:3])

    return render_template(template, title=parts['title'], toc=toc, body=parts['fragment'], name=name, meta=meta)

def spec_show(name):
    return render_rst(SPEC_DIR, name, spec_meta, 'spec/show.html')

def spec_show_txt(name):
    return render_rst(SPEC_DIR, name, spec_meta, None)

def proposal_show(name):
    return render_rst(PROPOSAL_DIR, name, proposal_meta, 'spec/proposal-show.html')

def proposal_show_txt(name):
    return render_rst(PROPOSAL_DIR, name, proposal_meta, None)

def spec_meta(meta):
    return helpers.get_metadata_from_meta(meta, SPEC_METATAGS, SPEC_LIST_METATAGS)

def proposal_meta(meta):
    return helpers.get_metadata_from_meta(meta, PROPOSAL_METATAGS, PROPOSAL_LIST_METATAGS)
