from flask import g, redirect, url_for


##############
# Legacy paths

LEGACY_FUNCTIONS_MAP={
    'announcements': 'blog_index',
    'download':      'downloads_list',
    'statusnotes':   'blog_index',
}

LEGACY_PAGES_MAP={
    'applications':           'volunteer/develop/applications',
    'bittorrent':             'docs/applications/bittorrent',
    'blockfile':              'docs/spec/blockfile',
    'bob':                    'docs/api/bob',
    'bounties':               'volunteer/bounties',
    'common_structures_spec': 'docs/spec/common_structures',
    'configuration':          'docs/spec/configuration',
    'datagrams':              'docs/spec/datagrams',
    'dev-guidelines':         'volunteer/guides/devguidelines',
    'donate':                 'volunteer/donate',
    'faq':                    'support/faq',
    'getinvolved':            'volunteer',
    'halloffame':             'about/halloffame',
    'how':                    'docs',
    'how_cryptography':       'docs/how/cryptography',
    'how_elgamalaes':         'docs/how/elgamalaes',
    'how_intro':              'docs/how/intro',
    'how_networkcomparisons': 'about/comparison',
    'how_networkdatabase':    'docs/how/networkdatabase',
    'how_peerselection':      'docs/how/peerselection',
    'how_threatmodel':        'docs/how/threatmodel',
    'how_tunnelrouting':      'docs/how/tunnelrouting',
    'how_garlicrouting':      'docs/how/garlicrouting',
    'i2cp':                   'docs/protocol/i2cp',
    'i2cp_spec':              'docs/spec/i2cp',
    'i2np':                   'docs/protocol/i2np',
    'i2np_spec':              'docs/spec/i2np',
    'i2pcontrol':             'docs/api/i2pcontrol',
    'i2ptunnel':              'docs/api/i2ptunnel',
    'intro':                  'about/intro',
    'jbigi':                  'misc/jbigi',
    'licenses':               'volunteer/develop/licenses',
    'monotone':               'volunteer/develop/monotone',
    'naming':                 'docs/naming',
    'newdevelopers':          'volunteer/guides/newdevelopers',
    'newtranslators':         'volunteer/guides/newtranslators',
    'ntcp':                   'docs/transport/ntcp',
    'papers':                 'research/papers',
    'performance':            'support/performance/future',
    'plugins':                'docs/plugins',
    'plugin_spec':            'docs/spec/plugin',
    'ports':                  'docs/ports',
    'protocols':              'docs/protocol',
    'roadmap':                'volunteer/roadmap',
    'sam':                    'docs/api/sam',
    'samv2':                  'docs/api/samv2',
    'samv3':                  'docs/api/samv3',
    'socks':                  'docs/api/socks',
    'streaming':              'docs/api/streaming',
    'team':                   'about/team',
    'techintro':              'docs/how/techintro',
    'todo':                   'volunteer/todo',
    'transport':              'docs/transport',
    'tunnel-alt':             'docs/tunnels/implementation',
    'tunnel-alt-creation':    'docs/spec/tunnel_creation',
    'tunnel_message_spec':    'docs/spec/tunnel_message',
    'udp':                    'docs/transport/ssu',
    'udp_spec':               'docs/spec/ssu',
    'unidirectional-tunnels': 'docs/tunnels/unidirectional',
    'updates':                'docs/spec/updates',
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
