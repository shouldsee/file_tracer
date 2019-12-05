import  decorator
from file_tracer import *
@decorator.decorator
def Dye(f,*args,**kwargs):
    p = Proxy()
    _args = get_file(args, p.hist)
    _kwargs = get_file(kwargs, p.hist)
    p.set_value( f(*_args,**_kwargs))

    return p

def get_file(ob, s):
    if isinstance(ob,File):
        s.add(ob)
    elif isinstance(ob, Proxy):
        s.update(ob.hist)
        ob = ob()
    elif isinstance(ob,(tuple,list)):
        ob = type(ob)([get_file( _ob,s) for _ob in ob])
    elif isinstance(ob,dict):
        d = dict()
        for (k,v) in ob.items():
            k = get_file(k,s)
            v = get_file(v,s)
            d[k] = v
        ob = d
    elif hasattr(ob,'_get_file'):
        ob._get_file(s)
    else:
        print(('[SKIPPING]',type(ob,),ob))
    return ob



class Proxy(object):
    def __init__(self, value=None):
        self._value = value
        self.hist = set()
    def __call__(self):
        while isinstance(self, Proxy):
            self=self._value
        return self
    def set_value(self,v):
        if isinstance(v,Proxy):
            v = v()
        self._value = v
    @property
    def value(self):
        return self()
        # self._foo
    

from file_tracer import FileTracer,InputFile,OutputFile,tree_as_string
from collections import Counter
with open(InputFile('input1.html'),'w') as f:
    f.write('123')
with open(InputFile('input2.html'),'w') as f:
    f.write('abc')

@Dye
def readInput(x):
    with open((x),'r') as f:
        return f.read()

@Dye
def middleStep(x):
    return readInput(x)

@Dye
def dumpOutput(x):
    s = middleStep(x)()
    d = Counter(s)
    of = OutputFile(x+'.count')
    with open( of,'w') as f:
        map(f.write,[str(x) for x in d.items()])
        # f.write(d.items())
    return of

@Dye
def main():
    p = dumpOutput(InputFile('input1.html'))
    print(p(),p.hist)
main()
