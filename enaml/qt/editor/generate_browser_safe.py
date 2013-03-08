import sys
import os
import re

try:
    filename = sys.argv[1]
    if os.path.exists(filename):
        html = open(filename, 'r').read()
        html = re.sub(r'\$\{.*\}/?', '', html)
        open(filename.split('.')[0] + '_safe.html', 'w').write(html)
    else:
        print "File does not exist."
except:
    print "Please specify a file."
