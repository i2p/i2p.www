import codecs
from docutils.core import (
    publish_doctree,
    publish_from_doctree,
    publish_parts,
)
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
    'lastupdated': None,
    }

SPEC_LIST_METATAGS = [
    ]


def spec_index():
    specs = []
    for f in os.listdir(SPEC_DIR):
        if f.endswith('.rst'):
            path = safe_join(SPEC_DIR, f)
            # read file header
            header = ''
            with codecs.open(path, encoding='utf-8') as fd:
                for line in fd:
                    header += line
                    if not line.strip():
                        break
            parts = publish_parts(source=header, source_path=SPEC_DIR, writer_name="html")
            meta = get_metadata_from_meta(parts['meta'])

            spec = {
                'name': f[:-4],
                'title': parts['title'],
            }
            spec.update(meta)
            specs.append(spec)

    specs.sort(key=lambda s: s['name'])
    return render_template('spec/index.html', specs=specs)

def spec_show(name, txt=False):
    # check if that file actually exists
    path = safe_join(SPEC_DIR, name + '.rst')
    if not os.path.exists(path):
        abort(404)

    # read file
    with codecs.open(path, encoding='utf-8') as fd:
        content = fd.read()

    if txt:
        # Strip out RST
        content = content.replace('.. meta::\n', '')
        content = content.replace('.. contents::\n\n', '')
        content = content.replace('.. raw:: html\n\n', '')
        content = content.replace('\n.. [', '\n[')
        content = content.replace(']_.', '].')
        content = content.replace(']_', '] ')
        # Change highlight formatter
        content = content.replace('{% highlight', "{% highlight formatter='textspec'")

    # render the post with Jinja2 to handle URLs etc.
    rendered_content = render_template_string(content)
    rendered_content = rendered_content.replace('</pre></div>', '  </pre></div>')

    if txt:
        # Send response
        r = make_response(rendered_content)
        r.mimetype = 'text/plain'
        return r

    # Render the ToC
    doctree = publish_doctree(source=rendered_content)
    bullet_list = doctree[1][1]
    doctree.clear()
    doctree.append(bullet_list)
    toc = publish_from_doctree(doctree, writer_name='html')

    # Remove the ToC from the main document
    rendered_content = rendered_content.replace('.. contents::\n', '')

    # publish the spec with docutils
    parts = publish_parts(source=rendered_content, source_path=SPEC_DIR, writer_name="html")
    meta = get_metadata_from_meta(parts['meta'])

    return render_template('spec/show.html', title=parts['title'], toc=toc, body=parts['fragment'], name=name, meta=meta)

def spec_show_txt(name):
    return spec_show(name, True)

def get_metadata_from_meta(meta):
    return helpers.get_metadata_from_meta(meta, SPEC_METATAGS, SPEC_LIST_METATAGS)
