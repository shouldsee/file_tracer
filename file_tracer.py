from functools import reduce
import os,sys
from path import Path
import path
import sys
# import trace
import asciitree
from asciitree.drawing import BOX_DOUBLE

import decorator
# import dill
import pyhash
hasher = pyhash.metro_64()
# import hasher = pyhash.metro_64()
# import pickle as dill
import dill
import inspect
import copy
from collections import defaultdict
from collections import OrderedDict as _dict#
# from collections import namedtuple
import collections

import logging
import warnings
from _ast_util import ast_proj
import numbers

try:
    ## py2
    unicode
except:
    ## py3
    unicode = str


def hash_tree(o):
    '''
    PY3 turns on hash randomisation by default. 
    Here a deterministic hash function is used to replace default hash function

    '''
    if hasattr(o,'_hash'):
        return o._hash()
    elif o is None:
        return None.__hash__()
    elif isinstance(o,dict):
        return hash_tree(tuple(sorted(o.items)))
    elif isinstance(o,(bytes,str)):
        return hasher(o)
    elif isinstance(o, list):
        return hash_tree(tuple(o))
    elif isinstance(o, tuple):
        return tuple.__hash__(tuple(map(hash_tree,o))) 
    elif isinstance(o, numbers.Number):
        return o
    elif isinstance(o, frozenset):
        return hash_tree(tuple(sorted(x for x in o)))
    elif isinstance(o,set):
        return hash_tree(frozenset(o))
    else:
        assert 0,('Unable to hash',type(o),repr(o))
# hash = 
_hash = hash_tree
# _hash = hash



def frame_default(frame=None):
    '''
    return the calling frame unless specified
    '''
    if frame is None:
        frame = inspect.currentframe().f_back.f_back ####parent of caller by default
    else:
        pass    
    return frame
def tree_as_string(d):
    if len(d)!=1:
        d=dict(ROOT=d)
    box_tr = asciitree.LeftAligned(draw=asciitree.BoxStyle(gfx=BOX_DOUBLE, horiz_len=1))(d)
    return box_tr

def tree(): return defaultdict(tree)

def visitPath(tr,path):
    for k in path:
        tr = tr[k]
def drill(d, k=None,s=None):
    if k is None:
        k = ()
    if s is None:
        s = []
    for _k,v in d.items():
        if isinstance(v,dict) and v:
            drill(v, k+(_k,), s)
        else:
            s.append(k+(_k,))
    return s



_os_stat_result_null = os.stat_result([0 for n in range(os.stat_result.n_sequence_fields)])
def os_stat_safe(fname):
    if file_not_empty(fname):
        return os.stat(fname)
    else:
        return _os_stat_result_null

def file_not_empty(fpath):  
    '''
    Source: https://stackoverflow.com/a/15924160/8083313
    '''
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0

    
class StampChanged(RuntimeWarning):
    pass
class File(Path):
    stamp = ()
    stat_result = _os_stat_result_null
    # stamp = _os_stat_result_null
    def __repr__(self,):
        return Path.__repr__(self)[:-1]+',st_mtime=%r,st_size=%r)'%(
            self.stat_result.st_mtime,
            self.stat_result.st_size,
            # is not None
            )
    def __init__(self,*a,**kw):
        # self.addTimeStamp()
        super(File,self).__init__(*a,**kw)
        # Path.__init__(self,*a,**kw)
        # self.stat_result = os_stat_safe(self)
        # self.stat_result = _os_stat_result_null
        # self.stat_result = os_stat_safe(self)
        # return 
    def addTimeStamp(self):
        self.stat_result = res = os_stat_safe(self)
        self.stamp = (res.st_mtime, res.st_size)
        return self

    def replace(self,k,v):
        return File(super(File,self).replace(k,v))
    def __hash__(self):
        return self._hash()
    def _hash(self):
        # return hash(tuple(sorted(vars(self).items())))
        # return _hash((Path.__hash__(self), self.stamp))
        return _hash((_hash(str(self)), self.stamp))
        # return hash((Path.__hash__(self),self.stamp))

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and str(self)==str(other)
        # hash(self)==hash(other)


class InputFile(File):
    def __init__(self,*a,**kw):
        super(InputFile,self).__init__(*a,**kw)

    pass

class OutputFile(File):
    def __init__(self,*a,**kw):
        super(OutputFile,self).__init__(*a,**kw)
    pass

class FileObject(object):
    # @property
    def addTimeStamp(self):
        return [x.addTimeStamp() for x in self.all_files]
    @property
    def output_files(self):
        return set([x for x in self.all_files if isinstance(x,OutputFile)])
    @property
    def input_files(self):
        return set([x for x in self.all_files if isinstance(x,InputFile)]) - {InputFile(x).addTimeStamp() for x in self.output_files}

class FileSet(set,FileObject):

    @property
    def all_files(self):
        return self
    def __hash__(self):
        return hash(tuple(sorted(list(self))))
        # return hash( hash(x) for x in (self))
        # return hash(frozenset(self))
    # @property
    # def output_files(self):
    #     return set([x for x in self.all_files if isinstance(x,OutputFile)])
    # @property
    # def input_files(self):
    #     return set([x for x in self.all_files if isinstance(x,InputFile)]) - {InputFile(x) for x in self.output_files}

class FileSetDict(dict,FileObject):

    @property
    def all_files(self):
        return reduce(lambda x,y: x|y, 
            [x for x in self.values() if isinstance(x,FileSet)],set())
    

# print(__name__,)
# logger = logging.getLogger('FileTracer',)
logger = logging.getLogger(__name__,)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.addHandler(handler)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
FunctionInput = collections.namedtuple('FunctionInput',[
    # 'func_code_co_code',
    # 'func_code_co_consts',

    'args','keywords','argValues','sortedKeywordValues'])

def getFuncId(func):
    return func.__code__
class FileTracer(FileObject,object):
    logger = logger
    class UsingCacheWarning(RuntimeWarning):
        pass
    class RecalcWarning(RuntimeWarning):
        pass
    class FirstRunWarning(RuntimeWarning):
        pass
    # DEBUG = 0
    def __init__(self, s = None, frame=None, DEBUG=0):
        # self.data = s or set()
        # self.all_files = set()
        self.file = os.path.realpath(
            inspect.getfile(frame_default(frame))+'.pkl'
            # inspect.getmodule(frame_default(frame)).__path__+'.pickle'
            )
        # self.file = inspect.stack()[-1][1]
        # assert 0,self.file
            # frame_default(frame).f_back.f_locals['__file__']+'.pickle')
        self.filename = frame_default(frame).f_code.co_filename
        # print(self.filename)
        self.clear(frame_default(frame))
        try:
            with open(self.file,'rb') as f:
                d = dill.load(f)
                self.__dict__ = d.__dict__
                # self.__setstate__(d.__dict__)
        except Exception as e:
            warnings.warn(str(e))
        self.DEBUG = DEBUG
        self.changed = 0

    def __call__(self,*a,**kw):
        return self.run(*a,**kw)

    def __len__(self):
        return self.byFuncCode.__len__()

    @property
    def size(self):
        return sum(len(x) for x in self.byFuncCode.values())
    def on(self):
        sys.settrace(self.trace_calls)
    def off(self):
        sys.settrace(None)
    def run(self, func, *a,**kw):
        self.on()
        result = func(*a,**kw)
        self.off()
        self.dump_to_file()
        return result

    def dump_to_file(self, file=None,strict=0):
        if not self.changed:
            return 
        if file is None:
            file = self.file
        try:
            if self.DEBUG:
                print(('[DUMPING]',file,len(self.byFuncCode)))
                # print(('[DUMPING]',file,len(self)))
            with open( file,'wb') as f:
                dill.dump(  self,f)
        except Exception as e:
            print('[ERR!!]unable to save:%s'%['[DUMPING]',file,len(self.byFuncCode)])
            warnings.warn(str(e))
            if strict:
                raise e
            # strict = True
        # return result

    def clear(self, frame=None):
        self.byFuncCode = dict()
        self.code2func = dict()
        self.lastCall = dict()
    # def __setstate__
        # self.byAst = dict()

    @property
    def fileSetByFunc(self):        
        return {k:v[0] for k,v in self.byFuncCode.items()}

    def getFileSetByFunc(self,func,*a,**kw):
        # return self.
        return self.byFuncCode[self.makeFunctionInputHash(func,a,kw)][0]

    @property
    def byFunc(self):
        # return {self.funcId(k) for k,v in self.byFuncCode.items()}
        return {self.code2func[k]:v for k,v in self.byFuncCode.items()}

    def getFuncCache(self,func):
        return self.byFuncCode[getFuncId(func._origin)]
    # @property
    # def byFuncCode(self):
    #     return {k.__code__:v for k,v in self.byFunc.items()}
    def trace_lines(self, frame, event, arg):

        # co = frame.f_code
        # func_name = co.co_name
        # line_no = frame.f_lineno
        # filename = co.co_filename
        # if co.co_name == '__init__':
        #     print(event,line_no,filename,co,arg)

        if event != 'return':
            return        
        co = frame.f_code
        func_name = co.co_name
        line_no = frame.f_lineno
        filename = co.co_filename
        # print(event,line_no,filename,co,arg)

        frame0 = frame
        # frames = []
        sets = []
        while True:
            # if frame.f_code not in self.byFuncCode:
            #     break
            if frame is None:
                break
            s = self.lastCall.get(frame.f_code,None)
            # s = self.byFuncCode.get(frame.f_code,None)
            sets.append(s) if s is not None else None
            frame = frame.f_back
        if not sets:
            return
        # print(path.__file__)
        for x in frame0.f_locals.values():
            if isinstance(x,File):
                [s.add(x) for s in sets]
                # if co.co_name not in ['addTimeStamp','hash_tree',]:
                #     # print((co.co_name,event,line_no,filename))
                #     # print((event,line_no,filename,co,arg))
                #     print(('aa',x,))                
    def trace_calls(self, frame, event, arg):
        # if frame.f_code not in self.byFuncCode:
        #     return
        if event != 'call':
            return
        else:            
            # if frame.f_code.co_filename not in [self.filename, __file__]:
            #     return
            # else:
            return self.trace_lines


    @property
    def all_files(self):
        return reduce(lambda x,y: x|y, [x.all_files for x in self.fileSetByFunc.values()], set())

    @staticmethod
    def _hash(x):
        if isinstance(x,tuple):
            return ',\n'.join([str( _hash(_x)) for _x in x])

        return str(_hash(x))
        # _hash = 
        # if DEBUG:
        # _hash = lambda x: bytes("%020d"%abs(hash(x))) +b'x'
        # _hash = lambda x:bytes([hash(x)])
        # _hash = lambda x:str( hash(x))
        # _hash = lambda x:

        # def _hash(x):
        #### pickled object cannot be loaded correctly
        #     s = dill.dumps(x);
        #     dill.loads(s)
        #     # print(len(s.split('\n')))
        #     # print(collections.Counter(s)['\n'])
        #     # print('\n' in s[:-1])
        #     return s
        # return dill.dumps(x)
    @staticmethod
    def makeFunctionInput(f,a,kw):
        # print('kw',kw,hash(tuple(sorted(kw.items()))))
        (args, varargs, keywords, defaults) = inspect.getargspec(f)
        # code = getattr(f,'_origin',f).__code__.co_code
        # print((hash(code),code,))
        _code = getattr(f,'_origin',f).__code__
        _kw = FunctionInput( 
            tuple(args or ()),
            tuple(keywords or ()), 
            tuple(a), 
            # tuple(sorted({}.items())),
            tuple(sorted(kw.items()))
            )
        # _kw = tuple(args) + tuple(a) + tuple(keywords  or ())+ tuple(sorted(kw.items()))
        assert '_FileSet' not in kw,(f,f.__code__)
        assert '_FileSet' not in args,(f,f.__code__)
        return _kw

    def makeFunctionInputHash(self,f,a,kw):
        return self._hash(self.makeFunctionInput(f,a,kw))
    @staticmethod
    def funcId(f):
        _code = getattr(f,'_origin',f).__code__
        return ( _code.co_code, _code.co_consts)

    def cache(self,func):
        @decorator.decorator
        def dec(f, *a,**kw):
            cache = self.byFuncCode.setdefault(
                self.funcId(f),
                {})
            _kw = self.makeFunctionInput( lambda x:x, a,kw)
            _hash = self._hash
            _fileSetKey = _hash(_kw)

            fileSetData , returnedData = cache.setdefault(    
                _fileSetKey,
                (FileSetDict(), FileSetDict()) )

            "old_file_set contains file touched during last run"
            _f = frame_default(None).f_back
            msg = (_f.f_lineno, _f.f_code)            
            using_cache =0 
            if self.DEBUG:
                print()
            if _fileSetKey not in fileSetData:
                firstRun = True
                if self.DEBUG:
                    print('[FIRST_RUN]')
                # new_file_set = FileSet()
            else:
                firstRun = False
                new_file_set = fileSetData[_fileSetKey]
                "This access is found in cache and returned a fileset"
                "_oldKey is meaningless if firstRun"
                # _oldKey = (_fileSetKey, _hash(new_file_set))
                _oldKey = u':'.join((_fileSetKey,_hash(new_file_set)))
                if self.DEBUG>=2:
                    for x in new_file_set:
                        print(str(x),x.stamp[0],x.__class__,)

                new_file_set.addTimeStamp()
                _newKey = u':'.join((_fileSetKey,_hash(new_file_set)))
                if self.DEBUG>=2:
                    for x in new_file_set:
                        print(str(x),x.stamp[0],x.__class__,)
                # _newKey = tuple((k,hash(v)) for k,v in _kw.items())                
                 ### record to be deleted
                # _oldValue = data[_oldKey] ### capture error
                if self.DEBUG>=2:
                    print("[ACCES_OLD]%r"%_oldKey)
                    print("[ACCES_NEW]%r"%_newKey)

                if _oldKey not in returnedData:
                    print(('OLDKEY',_oldKey,))
                    print(('new_file_set',new_file_set))
                     # list(returnedData.keys()))
                    for k in list(returnedData.keys()):
                        print(('LIST_KEYS',k))
                    assert 0, msg
                    # self._throw_debug_exception(_oldKey, returnedData)
                    # assert 0, msg

                if _newKey == _oldKey:
                    self.logger.info(self.FirstRunWarning("[USING_CACHE]%s"%list(msg)))
                    value =  returnedData[_oldKey]
                    using_cache = 1

            if not using_cache:
                if firstRun:
                    self.logger.info(self.FirstRunWarning("[FIRST_RUN]%s"%list(msg)))
                else:
                    self.logger.info(self.FirstRunWarning("[RECALC]%s"%list(msg)))

                "timestamp or argument changed, reexecute and remove old record"
                "recapture FileSet"
                self.lastCall[f.__code__] = new_file_set =  FileSet()
                value = f(*a,**kw)            
                new_file_set.addTimeStamp()
                fileSetData[ _fileSetKey ] = new_file_set
                #### reuse _fileSetKey avoids mutation in _kw
                # _newKey = (_fileSetKey, _hash(new_file_set))
                _newKey = u':'.join((_fileSetKey,_hash(new_file_set)))
                returnedData.pop(_oldKey,None) if not firstRun else None
                returnedData[_newKey] = value 
                if self.DEBUG>=2:
                    print("[ASSIGNING]:---\n%s\n---\n%s\n---"%(_newKey,value))
            self.changed = not using_cache
            return value


        gunc = dec(func)
        gunc.__name__ = gunc.__name__ + '_decorated'
        gunc._origin = func
        self.code2func[self.funcId(func)] = gunc
        return gunc

    @property
    def timeStampDict(self):
        d = {}
        for x in self.all_files:
            d[x] = os_stat_safe(x)
        return d

    # def __getitem__(self,func):
    @staticmethod
    def _throw_debug_exception( _oldKey, data,):
        # print (data.items()
        # for v in dill.loads(_oldKey)['_FileSet']: print(repr(v))
        for i,(k,v) in enumerate([(_oldKey,None)] + list(data.items())): 
            print(i,k,v)
            if not isinstance(k,unicode):
                continue
            print(i,v if not isinstance(v,FileSet) else "FileSet")
            for _k,v in (dill.loads(k).items()): 
                print(repr(_k),isinstance(v,FileSet))
                if isinstance(v,FileSet):
                    for _v in v :print(repr(_v))
                else:
                    print(_k,v)
            print()
            print(repr(k))
        # (_f.f_lineno, _f.f_code)
    @property
    def output_input_pairs(self):
        return [(x[0],x[-1]) for x in self.paths]
    @property
    def output_input_dict(self):
        d = defaultdict(set)
        for o,i in self.output_input_pairs:
            d[o].add(i)
        return d
    
    @property
    def treeByOutput(self):
        tr0 = tr = tree()
        for _path in self.paths:
            visitPath(tr,_path)
        return tr


'''
--------------------------------------------------------------
'''

