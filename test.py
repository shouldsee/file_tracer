
from file_tracer import FileTracer,InputFile,OutputFile,tree_as_string
from collections import Counter

tracer = FileTracer()

import time
import dill
v = InputFile('input1.html')
v.addTimeStamp()
s = dill.dumps(v)
time.sleep(0.02)
vout = dill.loads(s)
vout.addTimeStamp()
assert (v.stamp==vout.stamp),(v.stamp,vout.stamp)

time.sleep(0.02)
with open(v,'w') as f:f.write('test111111111')
vout = type(v)(v)
vout.addTimeStamp()
assert (v.stamp!=vout.stamp),(v.stamp,vout.stamp)
print v.stamp
print vout.stamp
# stat_result.st_mtime
print (hash(v))
v.addTimeStamp()
print(hash(v))
print (hash(vout))
print(v==vout)


with open(InputFile('input1.html'),'w') as f:
    f.write('123')
with open(InputFile('input2.html'),'w') as f:
    f.write('abc')

print("-"*50)
###################### TESTING  simple scenario
tracer.clear()
def readInput(x):
    with open((x),'r') as f:
        return f.read()

def middleStep(x):
    return readInput(x)

def dumpOutput(x):
    s = middleStep(x)
    d = Counter(s)
    fn = OutputFile(x+'.count')
    with open(fn,'w') as f:
        map(f.write,[str(x) for x in d.items()])
    return 

@tracer.cache
def main():
    dumpOutput(InputFile('input1.html'))
    # dumpOutput(InputFile('input2.html'))

tracer(main)
assert tracer.byFunc[main].output_files == {OutputFile(u'input1.html.count').addTimeStamp()},tracer.byFunc[main].output_files
assert tracer.byFunc[main].input_files == {InputFile(u'input1.html').addTimeStamp()},tracer.byFunc[main].input_files

assert tracer.output_files == {OutputFile(u'input1.html.count').addTimeStamp()},tracer.output_files
assert tracer.input_files == {InputFile(u'input1.html').addTimeStamp()},tracer.input_files


def main():
    dumpOutput(InputFile('input1.html'))

tracer.clear()
tracer(main)
assert main not in tracer.byFunc



print("-"*50)
tracer.clear()
tracer.DEBUG=1
def dumpOutput(x):
    s = middleStep(x)
    d = Counter(s)
    fn = OutputFile(x+'.count')
    with open(InputFile('input2.html'),'r') as f:
        pass
    # with open
    with open(fn,'w') as f:
        map(f.write,[str(x) for x in d.items()])
    return 
dumpOutput = tracer.cache(dumpOutput)
def main():
    dumpOutput(InputFile('input1.html'))
    time.sleep(0.02)
    dumpOutput(InputFile('input1.html'))
    time.sleep(0.02)
    with open('input2.html','w') as f: f.write('test111111111')
    dumpOutput(InputFile('input1.html'))
    dumpOutput(InputFile('input1.html'))
    # dumpOutput(InputFile('input2.html'))
tracer(main)
# for v in tracer.byFunc[dumpOutput].items():print v
print("-"*50)

# for v in tracer.byFunc[dumpOutput].all_files: print(repr(v))
# for v in tracer.byFunc[dumpOutput].items(): print(repr(v))




print v==vout
assert 0,"DONE"
# print tracer.data
print(tracer.paths)
from collections import defaultdict
def tree(): return defaultdict(tree)
tr =tree()
tr[1][2]={}
print tree_as_string({'rt':tracer.treeByOutput})
# print tree_as_string({'rt':tracer.byFiles})
# print _tree_as_string({'rt':tracer.byFuncs})


# print(tracer.data)