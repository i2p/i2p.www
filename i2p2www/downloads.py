from flask import abort, redirect, render_template
try:
    import json
except ImportError:
    import simplejson as json
from random import randint

from i2p2www import CURRENT_I2P_VERSION, MIRRORS_FILE

DEFAULT_MIRROR = {
    'protocol': 'https',
    'domain':   'download.i2p2.de',
    'org':      'meeh',
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
        protocol=obj['protocol']
        domain=obj['domain']
        path=obj['path']
        obj['url']='%s://%s%s' % (protocol, domain, path)
        if protocol not in ret:
            ret[protocol]={}
        ret[protocol][domain]=obj
    return ret

# List of downloads
def downloads_list():
    # TODO: read mirror list or list of available files
    return render_template('downloads/list.html', def_mirror=DEFAULT_MIRROR)

# Debian-specific page
def downloads_debian():
    return render_template('downloads/debian.html')

# Specific file downloader
def downloads_select(version, file):
    mirrors=read_mirrors()
    obj=[]
    for protocol in mirrors.keys():
        a={}
        a['name']=protocol
        a['mirrors']=mirrors[protocol]
        obj.append(a)
    return render_template('downloads/select.html', mirrors=obj, version=version, file=file)

def downloads_redirect(version, protocol, domain, file):
    mirrors=read_mirrors()
    if not protocol in mirrors:
        abort(404)
    mirrors=mirrors[protocol]
    data = {
        'version': version,
        'file': file,
        }
    if domain:
        if not domain in mirrors:
            abort(404)
        return render_template('downloads/redirect.html',
                               version=version, protocol=protocol, domain=domain, file=file,
                               url=mirrors[domain]['url'] % data)
    randomain = mirrors.keys()[randint(0, len(mirrors) - 1)]
    return render_template('downloads/redirect.html',
                           version=version, protocol=protocol, domain=domain, file=file,
                           url=mirrors[randomain]['url'] % data)
