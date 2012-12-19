from flask import g, redirect, url_for


##############
# Legacy paths

LEGACY_MAP={
    'download': 'downloads_list'
}

def legacy_show(f):
    lang = 'en'
    if hasattr(g, 'lang') and g.lang:
        lang = g.lang
    if f in LEGACY_MAP:
        return redirect(url_for(LEGACY_MAP[f], lang=lang))
    else:
        return redirect(url_for('site_show', lang=lang, page=f))

def legacy_meeting(id):
    return redirect(url_for('meetings_show', id=id, lang='en'))

def legacy_status(year, month, day):
    return redirect(url_for('blog_entry', lang='en', slug=('%s/%s/%s/status' % (year, month, day))))
