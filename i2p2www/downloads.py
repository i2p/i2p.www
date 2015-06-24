from flask import abort, redirect, render_template, request
try:
    import json
except ImportError:
    import simplejson as json
from random import randint

from i2p2www import CURRENT_I2P_VERSION, MIRRORS_FILE

DEFAULT_MIRROR = {
    'net': 'clearnet',
    'protocol': 'https',
    'domain':   'download.i2p2.de',
    'org':      'sigterm.no',
    'country':  'no',
}

DEFAULT_I2P_MIRROR = {
    'net': 'i2p',
    'protocol': 'http',
    'domain':   'whnxvjwjhzsske5yevyokhskllvtisv5ueokw6yvh6t7zqrpra2q.b32.i2p',
    'org':      'sigterm.no',
    'country':  'i2p',
}


###################
# Download handlers

# Read in mirrors from file
def read_mirrors():
    file = open(MIRRORS_FILE, 'r')
    dat = file.read()
    file.close()
    lines=dat.split('\n')
    ret={}
    for line in lines:
        try:
            obj=json.loads(line)
        except ValueError:
            continue
        if 'protocol' not in obj or 'domain' not in obj or 'path' not in obj:
            continue
        net=obj['net']
        protocol=obj['protocol']
        domain=obj['domain']
        path=obj['path']
        obj['url']='%s://%s%s' % (protocol, domain, path)
        if net not in ret:
            ret[net]={}
        if protocol not in ret[net]:
            ret[net][protocol]={}
        ret[net][protocol][domain]=obj
    return ret

# List of downloads
def downloads_list():
    # TODO: read mirror list or list of available files
    if request.headers.get('X-I2P-Desthash') and not request.headers.get('X-Forwarded-Server'):
        def_mirror = DEFAULT_I2P_MIRROR
    else:
        def_mirror = DEFAULT_MIRROR
    return render_template('downloads/list.html', def_mirror=def_mirror)

# Debian-specific page
def downloads_debian():
    return render_template('downloads/debian.html')

# Specific file downloader
def downloads_select(version, file):
    mirrors=read_mirrors()
    obj=[]
    for net in mirrors.keys():
        a={}
        a['key']=net
        a['name']=net
        a['protocols']=[]
        for protocol in mirrors[net].keys():
            b={}
            b['key']=protocol
            b['name']=protocol
            b['domains']=mirrors[net][protocol]
            a['protocols'].append(b)
        obj.append(a)
    return render_template('downloads/select.html', mirrors=obj, version=version, file=file)

def downloads_redirect(version, net, protocol, domain, file):
    mirrors=read_mirrors()
    if not net in mirrors:
        abort(404)
    mirrors=mirrors[net]
    data = {
        'version': version,
        'file': file,
        }

    if not protocol:
        protocol = mirrors.keys()[randint(0, len(mirrors) - 1)]
    if not protocol in mirrors:
        abort(404)
    mirrors=mirrors[protocol]

    if not domain:
        domain = mirrors.keys()[randint(0, len(mirrors) - 1)]
    if not domain in mirrors:
        abort(404)
    return render_template('downloads/redirect.html',
                           version=version, protocol=protocol, domain=domain, file=file,
                           url=mirrors[domain]['url'] % data)
