
if 0:
    import  decorator
    @decorator.decorator
    def Dye(f,*args,**kwargs):
        p = Proxy()
        args = get_file(args, p.hist)
        kwargs = get_file(kwargs, p.hist)
        res = f(*args,**kwargs)
        return Proxy(res)

    def get_file(ob, s):
        if isinstance(ob,File):
            s.add(ob)
        elif isinstance(ob, Proxy):
            s.update(ob.hist)
            return ob.value
        elif isinstance(ob,list):
            return [get_file( _ob,s) for _ob in ob]
        elif isinstance(ob,dict):
            # dict([(k,v)])
            d = dict()
            for (k,v) in ob.items():
                k = get_file(k,s)
                v = get_file(v,s)
                d[k] = v
            return d
        elif hasattr(ob,'_get_file'):
            ob._get_file(s)
        else:
            print(('[SKIPPING]',type(ob,),ob))



class Proxy(object):
    def __init__(self, value=None):
        self.value = value
        self.hist = set()
    def __call__(self):
        return self.value


class _Obsolete_FileTracer(object):
    def __init__(self, s = None):
        # self.data = s or set()
        self.all_files = set()
        self.data = dict()
        self.byFunc = dict()
        self.byFiles = dict()
    def __call__(self, func, *a,**kw):
        sys.settrace(self.trace_calls)
        result = func(*a,**kw)
        sys.settrace(None)
        return result
    def trace_calls(self, frame, event, arg):
        print(path.__file__)
        for x in frame.f_locals.values():
            if isinstance(x,File):
                self.all_files.add(x)
                _f = frame
                # if _f.f_code.co_filename== (path.__file__[:-1]):
                if _f.f_code is Path.__init__.func_code:
                   _f = _f.f_back
                    # else:
                    #     continue
                else:
                    print(_f.f_code,)
                    pass
                    # assert 0, _f.f_code
                if isinstance(x,InputFile):
                    _path = self.byFunc.setdefault(_f.f_code,{})
                    _path[x] = {}
                    while True:
                        _fb = _f.f_back
                        if _fb is None:
                            break
                        _d = self.byFunc.setdefault(_fb.f_code,{})
                        _d[_f.f_code] = _path
                        _path = _d
                        _f = _f.f_back
                    self.data[x] = _path
                elif isinstance(x,OutputFile):
                    self.byFunc.setdefault(_f.f_code,{})[x] = {}
                    # self.byFiles.setdefault(x,{})[_f.f_code]={}
                    self.byFiles.setdefault(x,[]).append(_f.f_code)
                    # ]={}
                    # .append(_f.f_code)
    @property
    def paths(self):
        lst = []
        i = 0
        visited = set()
        for outFile, fs in self.byFiles.iteritems():
            for f in fs:
                res = drill(self.byFunc[f],k=(f,))
                for x in res:
                    i+=1
                    if isinstance(x[-1],InputFile):
                    # if outFile is not x[-1]:
                        lst.append((outFile,) + x)
                        visited.add(x[-1])
            visited.add(outFile)
        for extra in self.all_files - visited:
            if isinstance(extra,InputFile):
                lst.append((None,extra))
            elif isinstance(extra,OutputFile):
                lst.append((extra,None))
        return lst
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
