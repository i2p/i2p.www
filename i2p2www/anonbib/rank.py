# Make rankings of papers and authors for automatic classification of content hotness

# Google Scholar address
# http://scholar.google.com/scholar?as_epq=

# Take care of the caching setup
cache_expire = 60*60*24*30 # 30 days

# Checks
import config
import os
import sys
from os.path import exists, isdir, join, getmtime
from os import listdir, remove

def remove_old():
   # Remove all old cached files
   filenames = listdir(cache_folder())
   from time import time
   now = time()
   for f in filenames:
      pf = join(cache_folder(), f)
      time_mt =  getmtime(pf)
      if now - time_mt > cache_expire: # 30 days
         remove(pf)

def cache_folder():
   r = join(config.OUTPUT_DIR, config.CITE_CACHE_DIR)
   if not exists(r):
      os.makedirs(r)
   assert isdir(r)
   return r

import re
from urllib2 import urlopen, build_opener
from urllib import quote
from datetime import date
import hashlib

# A more handy hash
def md5h(s):
   m = hashlib.md5()
   m.update(s)
   return m.hexdigest()

format_tested = 0

def getPageForTitle(title, cache=True, update=True, save=True):
   #Returns (citation-count, scholar url) tuple, or (None,None)
   global format_tested
   if not format_tested and update:
      format_tested = 1
      TestScholarFormat()

   # Do not assume that the title is clean
   title = re.sub("\s+", " ", title)
   title = re.sub("[^'a-zA-Z0-9\. \-\/:]", "", title)
   title = re.sub("'\/", " ", title)

   # We rely on google scholar to return the article with this exact title
   gurl = "http://scholar.google.com/scholar?as_q=&as_epq=%s&as_occt=title"

   url = gurl % quote(title)

   # Access cache or network
   if exists(join(cache_folder(), md5h(url))) and cache:
      return url, file(join(cache_folder(), md5h(url)),'r').read()
   elif update:
      print "Downloading rank for %r."%title

      # Make a custom user agent (so that we are not filtered by Google)!
      opener = build_opener()
      opener.addheaders = [('User-agent', 'Anon.Bib.0.1')]

      print "connecting..."
      connection = opener.open(url)
      print "reading"
      page = connection.read()
      print "done"
      if save:
         file(join(cache_folder(), md5h(url)),'w').write(page)
      return url, page
   else:
      return url, None

def getCite(title, cache=True, update=True, save=True):
   url, page = getPageForTitle(title, cache=cache, update=update, save=save)
   if not page:
      return None,None

   # Check if it finds any articles
   if len(re.findall("did not match any articles", page)) > 0:
      return (None, None)

   # Kill all tags!
   cpage = re.sub("<[^>]*>", "", page)

   # Add up all citations
   s = sum([int(x) for x in re.findall("Cited by ([0-9]*)", cpage)])
   return (s, url)

def getPaperURLs(title, cache=True, update=True, save=True):
   url, page = getPageForTitle(title, cache=cache, update=update, save=save)
   if not page:
      return []
   pages = re.findall(r'\&\#x25ba\;.*class=fl href="([^"]*)"', page)
   return pages

def get_rank_html(title, years=None, base_url=".", update=True,
                  velocity=False):
   s,url = getCite(title, update=update)

   # Paper cannot be found
   if s is None:
      return ''

   html = ''

   url = url.replace("&","&amp;")

   # Hotness
   H,h = 50,5
   if s >= H:
      html += '<a href="%s"><img src="%s/gold.gif" alt="More than %s citations on Google Scholar" title="More than %s citations on Google Scholar" /></a>' % (url,base_url,H,H)
   elif s >= h:
      html += '<a href="%s"><img src="%s/silver.gif" alt="More than %s citations on Google Scholar" title="More than %s citations on Google Scholar" /></a>' % (url,base_url,h,h)

   # Only include the velocity if asked.
   if velocity:
      # Velocity
      d = date.today().year - int(years)
      if d >= 0:
         if 2 < s / (d +1) < 10:
            html += '<img src="%s/ups.gif" />' % base_url
         if 10 <= s / (d +1):
            html += '<img src="%s/upb.gif" />' % base_url

   return html

def TestScholarFormat():
   # We need to ensure that Google Scholar does not change its page format under our feet
   # Use some cases to check if all is good
   print "Checking google scholar formats..."
   stopAndGoCites = getCite("Stop-and-Go MIXes: Providing Probabilistic Anonymity in an Open System", False)[0]
   dragonCites = getCite("Mixes protected by Dragons and Pixies: an empirical study", False, save=False)[0]

   if stopAndGoCites in (0, None):
      print """OOPS.\n
It looks like Google Scholar changed their URL format or their output format.
I went to count the cites for the Stop-and-Go MIXes paper, and got nothing."""
      sys.exit(1)

   if dragonCites != None:
      print """OOPS.\n
It looks like Google Scholar changed their URL format or their output format.
I went to count the cites for a fictitious paper, and found some."""
      sys.exit(1)

def urlIsUseless(u):
   if u.find("freehaven.net/anonbib/") >= 0:
      # Our own cache is not the primary citation for anything.
      return True
   elif u.find("owens.mit.edu") >= 0:
      # These citations only work for 'members of the MIT community'.
      return True
   else:
      return False

URLTYPES=[ "pdf", "ps", "txt", "ps_gz", "html" ]

if __name__ == '__main__':
   # First download the bibliography file.
   import BibTeX
   suggest = False
   if sys.argv[1] == 'suggest':
      suggest = True
      del sys.argv[1]

   config.load(sys.argv[1])
   if config.CACHE_UMASK != None:
      os.umask(config.CACHE_UMASK)
   bib = BibTeX.parseFile(config.MASTER_BIB)
   remove_old()

   print "Downloading missing ranks."
   for ent in bib.entries:
      getCite(ent['title'], cache=True, update=True)

   if suggest:
      for ent in bib.entries:
         haveOne = False
         for utype in URLTYPES:
            if ent.has_key("www_%s_url"%utype):
               haveOne = True
               break
         if haveOne:
            continue
         print ent.key, "has no URLs given."
         urls = [ u for u in getPaperURLs(ent['title']) if not urlIsUseless(u) ]
         for u in urls:
            print "\t", u

