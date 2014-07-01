"""
Make Diffs for the GOMH project

Run from the ./backups/ directory, where all of the gomh_0*.py files are located.
"""

import difflib

for i in range(0, 17):
  d = difflib.HtmlDiff(wrapcolumn=60)
  o = d.make_file(open('gomh_%03d.py' % i).read().split('\n'), open('gomh_%03d.py' % (i+1)).read().split('\n'))

  open('diff/diff_%03d.html' % i, 'w').write(o)


