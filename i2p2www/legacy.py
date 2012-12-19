from flask import g, redirect, url_for


##############
# Legacy paths

LEGACY_FUNCTIONS_MAP={
    'download': 'downloads_list'
}

LEGACY_PAGES_MAP={
    'bounties': 'volunteer/bounties',
    'getinvolved': 'volunteer',
    'faq': 'support/faq',
}

def legacy_show(f):
    lang = 'en'
    if hasattr(g, 'lang') and g.lang:
        lang = g.lang
    if f in LEGACY_FUNCTIONS_MAP:
        return redirect(url_for(LEGACY_FUNCTIONS_MAP[f], lang=lang))
    elif f in LEGACY_PAGES_MAP:
        return redirect(url_for('site_show', lang=lang, page=LEGACY_PAGES_MAP[f]))
    else:
        return redirect(url_for('site_show', lang=lang, page=f))

def legacy_meeting(id):
    return redirect(url_for('meetings_show', id=id, lang='en'))

def legacy_status(year, month, day):
    return redirect(url_for('blog_entry', lang='en', slug=('%s/%s/%s/status' % (year, month, day))))
