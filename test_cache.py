import unittest2
import path
from file_tracer import FileTracer,OutputFile
tracer = FileTracer(DEBUG=2)

# TEMPDIR = path.Path(__file__ +'.build.temp').makedirs_p().realpath()
class SharedObject(object):
	DIR = path.Path(__file__ +'.build.temp').makedirs_p().realpath()
	pass

@tracer.cache
def job1(num):
	print('RUNNING',job1.__name__, num)
	with open(OutputFile( SharedObject.DIR /'%s.txt.temp'%num),'w') as f:
		f.write('a'*num)
	return num


def main():
	job1(1)
	job1(2)
	job1(3)
	
if __name__ == '__main__':
	tracer.run(main)
	import sys
	sys.stdout.write(str(tracer.size)+'\n')
	# print('-'*10)
	# print(str(tracer.__len__()))



# class BaseCase(unittest2.TestCase,SharedObject):
#     def test_cache(self):
#     	tracer.run(main)
#     	tracer.dump_to_file()
#     	print((tracer.byFuncCode.__len__(),))
#     	# del main
#     	tracer.run(main)
#     	assert tracer.byFuncCode.__len__() == 3
#     	# print((tracer.byFuncCode.__len__(),))


#     #     import test_cache
#     #     test_cache
#         # from test_cache i
#     pass
# import pdb
# import traceback
# def debugTestRunner(post_mortem=None):
#     """unittest runner doing post mortem debugging on failing tests"""
#     if post_mortem is None:
#         post_mortem = pdb.post_mortem
#     class DebugTestResult(unittest2.TextTestResult):
#         def addError(self, test, err):
#             # called before tearDown()
#             traceback.print_exception(*err)
#             post_mortem(err[2])
#             super(DebugTestResult, self).addError(test, err)
#         def addFailure(self, test, err):
#             traceback.print_exception(*err)
#             post_mortem(err[2])
#             super(DebugTestResult, self).addFailure(test, err)
#     return unittest2.TextTestRunner(resultclass=DebugTestResult)


# if __name__ == '__main__':

#     with SharedObject.DIR:
#         unittest2.main(testRunner=debugTestRunner())


# # if __name__ =='__main__':
# # 	tracer.run(main)

