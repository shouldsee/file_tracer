#import jinja2
#from pymisca.ext
from pymisca.ext import jf2
import jinja2
_open = open
with open("README.md",'w') as f:
	s = jf2(open('README.md.template','r').read(),)
	f.write(s)
#.render(**locals())
