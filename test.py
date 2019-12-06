# try:
import unittest2
# except:
    # import unittest as unittest2

from file_tracer import InputFile, OutputFile, FileTracer,FileSetDict
import time
from path import Path
import collections
import os
# import pickle
import pickle as dill
# import dill
__file__ = os.path.realpath(__file__)
class SharedObject(object):
    DIR = Path('build').makedirs_p()

def readInput(x):
    with open((x),'r') as f:
        return f.read()

def middleStep(x):
    return readInput(x)

# @tracer.cache
def dumpOutput(x):
    s = middleStep(x)
    d = collections.Counter(s)
    fn = OutputFile(x+'.count')
    with open(fn,'w') as f:
        map(f.write,[str(x) for x in d.items()])
    return    

    # pass

class BaseCase(unittest2.TestCase,SharedObject):
    pass
    def test_init(self):
        # with self.DIR:
        with open(InputFile('input1.html'),'w') as f:
            f.write('123')
        with open(InputFile('input2.html'),'w') as f:
            f.write('abc')        
    def test_tamp(self):
        # with self.DIR:
        tracer = FileTracer()
        v = InputFile('input1.html')
        v.addTimeStamp()

        time.sleep(0.02)
        vout = InputFile(v)
        vout.addTimeStamp()
        assert (v.stamp==vout.stamp),(v.stamp,vout.stamp)    

        time.sleep(0.02)
        with open(v,'w') as f:f.write('test111111111')
        vout = type(v)(v)
        vout.addTimeStamp()
        assert (v.stamp!=vout.stamp),(v.stamp,vout.stamp)

    def test_simple(self):
        # with self.DIR:
        tracer = FileTracer()
 
        @tracer.cache
        def main():
            dumpOutput(InputFile('input1.html'))
        
        tracer(main)
        assert tracer.fileSetByFunc[main].output_files == {OutputFile(u'input1.html.count').addTimeStamp()},tracer.fileSetByFunc[main].output_files
        assert tracer.fileSetByFunc[main].input_files == {InputFile(u'input1.html').addTimeStamp()},tracer.fileSetByFunc[main].input_files

        assert tracer.output_files == {OutputFile(u'input1.html.count').addTimeStamp()},tracer.output_files
        assert tracer.input_files == {InputFile(u'input1.html').addTimeStamp()},tracer.input_files

        tracer.clear()
        assert main not in tracer.byFunc

    def test_log(self):
        tracer = FileTracer() 
        # with self.DIR:
        @tracer.cache
        def dumpOutput(x):
            s = middleStep(x)
            d = collections.Counter(s)
            fn = OutputFile(x+'.count')
            with open(InputFile('input2.html'),'r') as f:
                pass
            # with open
            with open(fn,'w') as f:
                map(f.write,[str(x) for x in d.items()])        
                # assert 0
        def main():            
            dumpOutput(InputFile('input1.html'))
            time.sleep(0.02)
            dumpOutput(InputFile('input1.html'))
            time.sleep(0.02)
            with open('input2.html','w') as f: f.write('test111111111')
            dumpOutput(InputFile('input1.html'))
            dumpOutput(InputFile('input1.html'))
            dumpOutput(InputFile('input2.html'))
        with self.assertLogs('file_tracer',level='INFO') as logs:
            tracer.run(main)
        # logs.output
        regs = [
            'FIRST_RUN',
            'USING_CACHE',
            'RECALC',
            'USING_CACHE',
            'FIRST_RUN',
            ]
        for logText,reg in zip(logs.output,regs):
            pass
            self.assertRegex(logText, reg)
        # dill.loads(tracer.fileSetByFunc.values()[0])
        for k,fileSetDict in tracer.fileSetByFunc.items():
            print (k)
            print (fileSetDict.input_files)
            print (fileSetDict.output_files)
            for _k , fsd in fileSetDict.items():
                print ('-'*50)
                print (dill.loads(_k))
                print (fsd.input_files)
                print (fsd.output_files)

        pass
import pdb
import traceback
def debugTestRunner(post_mortem=None):
    """unittest runner doing post mortem debugging on failing tests"""
    if post_mortem is None:
        post_mortem = pdb.post_mortem
    class DebugTestResult(unittest2.TextTestResult):
        def addError(self, test, err):
            # called before tearDown()
            traceback.print_exception(*err)
            post_mortem(err[2])
            super(DebugTestResult, self).addError(test, err)
        def addFailure(self, test, err):
            traceback.print_exception(*err)
            post_mortem(err[2])
            super(DebugTestResult, self).addFailure(test, err)
    return unittest2.TextTestRunner(resultclass=DebugTestResult)


if __name__ == '__main__':

    with SharedObject.DIR:
        unittest2.main(testRunner=debugTestRunner())

