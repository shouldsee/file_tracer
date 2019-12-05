import textwrap,ast
from ast import NodeTransformer

def ast_next_func(node):
    '''
    return the first Lambda or FunctionDef
    '''
    for x in ast.walk(node):
        if isinstance(x, ast.FunctionDef) or isinstance(x, ast.Lambda):
            return x
    assert 0
    
class RemoveConst(NodeTransformer):
    '''
    Remove the constants expression in ast tree
    '''
    def visit_Expr(self,x):
        # print(x)
        if isinstance(x.value, (ast.Num, ast.Str,  ast.Ellipsis)):
            # print x.value
            return
        else:
            return x
        # return ast.AST()

def get_entryline(source):
    exprs = ast.parse(source).body
    for x in exprs:
        if isinstance(x,ast.If):
            if ast.dump(x.test) == "Compare(left=Name(id='__name__', ctx=Load()), ops=[Eq()], comparators=[Str(s='__main__')])":
                # print (x.lineno,x.col_offset)
                x = x.test
                # print (x.lineno,x.col_offset)
                return x.lineno -1
    return -1
        
def ast_proj(source):
    x = ast.parse(textwrap.dedent(source),mode='exec')
    x = ast_next_func(x)
    RemoveConst().visit(x)
#     del x.args[:]
    del x.args
    x = ast.dump(x,include_attributes=False,)
    return x


if __name__ == '__main__':
    s1 = "frame.f_locals['_symbolicInputNode'] = symin  =  RawNode(lambda self:(\nNone),\n        _dict(), _dict(),0,frame,1,'_symbolicInputNode',None)\n"
    s2 = "\n     RawNode(lambda self:None,\n        _dict(), _dict(),0,frame,1,'_symbolicInputNode',None)\n"
    assert ast_proj(s1) == ast_proj(s2),(s1,s2)


    s1 = '''
    def f(x):
        b = 2+3
        return b
    '''
    s2 = '''
        def f(x):
            b = 2+3
            return b
    '''
    assert ast_proj(s1) == ast_proj(s2),(s1,s2)

    s1 = '''
    def f(x):
        b = 2+3
        return b
    '''
    s2 = '''
        def f(x):
            "someconst"
            b = 2+3
            "otherstuff"
            return b

    '''
    v1,v2 = ast_proj(s1),ast_proj(s2)
    assert v1==v2,(v1,v2)

    s1 = '''
    def f(x):
        b = 2+3
        return b
    '''
    s2 = '''
        def f(x):
            {doc}
            "someconst"
            b = 2+3
            "otherstuff"
            return b

    '''.format(doc="'''test'''")
    v1,v2 = ast_proj(s1),ast_proj(s2)
    assert v1==v2,(s1,s2)

    # def source_is_same(s1,s2):
    #     return 


    # assert ast_proj(s1) == ast_proj(s2),(s1,s2)