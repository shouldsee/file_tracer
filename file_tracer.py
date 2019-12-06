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
import pickle as dill
import inspect
import copy
from collections import defaultdict
from collections import OrderedDict as _dict#
# from collections import namedtuple
import collections

import logging
import warnings
from _ast_util import ast_proj
# import linecache

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
        Path.__init__(self,*a,**kw)
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
        # return hash(tuple(sorted(vars(self).items())))
        return hash((Path.__hash__(self), self.stamp))
        # return hash((Path.__hash__(self),self.stamp))

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and str(self)==str(other)
        # hash(self)==hash(other)


class InputFile(File):
    pass

class OutputFile(File):
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
FunctionInput = collections.namedtuple('FunctionInput',['args','keywords','argValues','sortedKeywordValues'])
class FileTracer(FileObject,object):
    logger = logger
    class UsingCacheWarning(RuntimeWarning):
        pass
    class RecalcWarning(RuntimeWarning):
        pass
    class FirstRunWarning(RuntimeWarning):
        pass
    DEBUG = 0
    def __init__(self, s = None, frame=None):
        # self.data = s or set()
        # self.all_files = set()
        self.file = os.path.realpath(
            inspect.getfile(frame_default(frame))+'.pickle'
            )
        # assert 0,sef
            # frame_default(frame).f_back.f_locals['__file__']+'.pickle')
        self.clear(frame_default(frame))

    def __call__(self,*a,**kw):
        return self.run(*a,**kw)

    def run(self, func, *a,**kw):
        try:
            with open(self.file,'rb') as f:
                d = dill.load(f)
                self.__setstate__(d.__dict__)
        except Exception as e:
            warnings.warn(str(e))

        sys.settrace(self.trace_calls)
        result = func(*a,**kw)
        sys.settrace(None)

        try:
            with open(self.file,'wb') as f:
                dill.dump(self,f)
        except Exception as e:
            warnings.warn(str(e))
        return result
        
    def clear(self, frame=None):
        self.byFuncCode = dict()
        self.code2func = dict()
        self.lastCall = dict()
    # def __setstate__
        # self.byAst = dict()

    @property
    def fileSetByFunc(self):
        return {k:v[0] for k,v in self.byFunc.items()}
    @property
    def byFunc(self):
        return {self.code2func[k]:v for k,v in self.byFuncCode.items()}

    # @property
    # def byFuncCode(self):
    #     return {k.__code__:v for k,v in self.byFunc.items()}

    def trace_calls(self, frame, event, arg):
        frame0 = frame
        # frames = []
        sets = []
        while True:
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

    @property
    def all_files(self):
        return reduce(lambda x,y: x|y, [x.all_files for x in self.fileSetByFunc.values()], set())

    def cache(self,func):
        @decorator.decorator
        def dec(f, *a,**kw):
            (args, varargs, keywords, defaults) = inspect.getargspec(f)
            _kw = FunctionInput(tuple(args or ()),tuple(keywords or ()), tuple(a), tuple(sorted(kw.items())))
            # _kw = tuple(args) + tuple(a) + tuple(keywords  or ())+ tuple(sorted(kw.items()))
            assert '_FileSet' not in kw,(f,f.func_code)
            assert '_FileSet' not in args,(f,f.func_code)
            _hash = dill.dumps
            # if DEBUG:
            # _hash = lambda x: bytes("%020d"%abs(hash(x))) +b'x'
            _hash = lambda x:bytes(hash(x))
            # _hash = lambda x:

            # def _hash(x):
            #### pickled object cannot be loaded correctly
            #     s = dill.dumps(x);
            #     dill.loads(s)
            #     # print(len(s.split('\n')))
            #     # print(collections.Counter(s)['\n'])
            #     # print('\n' in s[:-1])
            #     return s

            _fileSetKey = _hash(_kw)

            fileSetData , returnedData = dataByFunc
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

                "_oldKey is meaningless if firstRun"
                # _oldKey = (_fileSetKey, _hash(new_file_set))
                _oldKey = b''.join((_fileSetKey,_hash(new_file_set)))
                if self.DEBUG>=2:
                    for x in new_file_set:
                        print(str(x),x.stamp[0],x.__class__,)

                new_file_set.addTimeStamp()
                _newKey = b''.join((_fileSetKey,_hash(new_file_set)))
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
                    self._throw_debug_exception(_oldKey, returnedData)
                    assert 0, msg

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
                _newKey = b''.join((_fileSetKey,_hash(new_file_set)))
                returnedData.pop(_oldKey,None) if not firstRun else None
                returnedData[_newKey] = value 
                if self.DEBUG>=2:
                    print("[ASSINGING]%r"%_newKey)

            return value

        # linecache.checkcache(func.func_code.co_filename)
        # dataByAst = self.byAst.setdefault(
        #     ast_proj(inspect.getsource(func)),
        #     FileSetDict())
        dataByFunc = self.byFuncCode.setdefault(
            func.__code__,
            # func.func_code,
            # ast_proj(inspect.getsource(func)),
            (FileSetDict(), FileSetDict()) )
        gunc = dec(func)
        gunc.__name__ = gunc.__name__ + '_decorated'
        gunc._origin = func
        # self.fileSetbyFunc[gunc] = dataByAst[0]
        self.code2func[func.__code__] = gunc
        # self.func2code[gunc] = (func,func.__code__)
        # self.byFunc[gunc] = dataByFunc

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
        for i,(k,v) in enumerate([(_oldKey,None)] + data.items()): 
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

