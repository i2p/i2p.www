from flask import redirect, render_template
try:
    import json
except ImportError:
    import simplejson as json
from random import randint

from i2p2www import CURRENT_I2P_VERSION, MIRRORS_FILE


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
        if 'protocol' not in obj:
            continue
        protocol=obj['protocol']
        if protocol not in ret:
            ret[protocol]=[]
        ret[protocol].append(obj)
    return ret

# List of downloads
def downloads_list():
    # TODO: read mirror list or list of available files
    return render_template('downloads/list.html')

# Specific file downloader
def downloads_select(version, file):
    if (file == 'debian'):
        return render_template('downloads/debian.html', file=file)
    mirrors=read_mirrors()
    data = {
        'version': version,
        'file': file,
        }
    obj=[]
    for protocol in mirrors.keys():
        a={}
        a['name']=protocol
        a['mirrors']=mirrors[protocol]
        for mirror in a['mirrors']:
            mirror['url']=mirror['url'] % data
        obj.append(a)
    return render_template('downloads/select.html', mirrors=obj, version=version, file=file)

def downloads_redirect(version, protocol, file, mirror):
    mirrors=read_mirrors()
    if not protocol in mirrors:
        abort(404)
    mirrors=mirrors[protocol]
    data = {
        'version': version,
        'file': file,
        }
    if mirror:
        return redirect(mirrors[mirror-1]['url'] % data)
    return redirect(mirrors[randint(0, len(mirrors) - 1)]['url'] % data)
