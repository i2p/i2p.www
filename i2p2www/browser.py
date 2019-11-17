from flask import redirect, render_template, request
from i2p2www import CURRENT_I2P_VERSION, MIRRORS_FILE

def browser_frontpage():
  useragent = request.headers.get('User-Agent')
  osname = "unknown"
  if 'Mac' in useragent:
    osname = "macosx"
  elif 'Win' in useragent:
    osname = "windows"
  elif 'Linux' in useragent:
    osname = "linux"
  return render_template('site/browser/_front.html', user_agent=useragent, detected_os=osname)

def browser_intro():
  return render_template('site/browser/intro.html')

def browser_download():
  return render_template('site/browser/download.html')

def browser_releasenotes():
  return render_template('site/browser/releasenotes.html')

def browser_roadmap():
  return render_template('site/browser/roadmap.html')

#def browser_known_issues():
#  return render_template('site/browser/known_issues.html')

#def browser_troubleshooting():
#  return render_template('site/browser/troubleshooting.html')

#def browser_updating():
#  return render_template('site/browser/updating.html')

def browser_develop():
  return render_template('site/browser/develop.html')

def browser_donate():
  return render_template('site/browser/donate.html')


def browser_faq():
  if request.headers.get('X-I2P-Desthash') and not request.headers.get('X-Forwarded-Server'):
    show_i2p_links = True
  else:
    show_i2p_links = False
  return render_template('site/browser/faq.html', is_i2p_internal=show_i2p_links)


