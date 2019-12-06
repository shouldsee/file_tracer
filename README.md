

1. FileTracer: A utility object to trace file interaction with time/size-stamping

Traditional caching [(1)](https://github.com/python/cpython/blob/30afc91f5e70cf4748ffac77a419ba69ebca6f6a/Lib/functools.py#L485),[(2)](https://stackoverflow.com/a/49883466/8083313) works by capturing function arguments, which 
is in-adequate if the function reads and outputs to a external file.
**FileTracer** seeks to capture file depedency by following 
two custom classes `file_tracer.InputFile()` and `file_tracer.OutputFile()`.
Upon detection, files are stored for this particular function call, so
that further function call would recaculate if any file is modified e.g.:
by removal of a output file.

Notes:
  - this package has not yet been optimised for speed yet.
  


```python

import collections
import time
from file_tracer import InputFile,OutputFile,FileTracer
from path import Path
tracer = FileTracer()

with Path('build').makedirs_p():
	with open(InputFile('input1.html'),'w') as f:
	    f.write('123')
	with open(InputFile('input2.html'),'w') as f:
	    f.write('abc')      
	def readInput(x):
	    with open((x),'r') as f:
	        return f.read()

	@tracer.cache
	def dumpOutput(x):
		s = readInput(x)
		d = collections.Counter(s)
		fn = OutputFile(x+'.count')

		### merely referencing the file is enough to log dependency
		with open(InputFile('input2.html'),'r') as f:
		    pass
		# with open
		with open(fn,'w') as f:
		    map(f.write,[str(x) for x in d.items()])        
	    # assert 0
	def main():            
		dumpOutput(InputFile('input1.html'))  ## first_run
		time.sleep(0.02) 
		dumpOutput(InputFile('input1.html'))  ## using_cache
		time.sleep(0.02)
		with open('input2.html','w') as f: f.write('test111111111') ## change implicit input
		dumpOutput(InputFile('input1.html'))  ## recalc
		dumpOutput(InputFile('input1.html'))  ## using_cache
		dumpOutput(InputFile('input2.html'))  ## first_run
	tracer.run(main)
#2019-12-06 00:08:21,038 - INFO - [FIRST_RUN][29, <code object main at 0x7fdbffc29030, file "example.py", line 28>]
#2019-12-06 00:08:21,095 - INFO - [USING_CACHE][31, <code object main at 0x7fdbffc29030, file "example.py", line 28>]
#2019-12-06 00:08:21,139 - INFO - [RECALC][34, <code object main at 0x7fdbffc29030, file "example.py", line 28>]
#2019-12-06 00:08:21,177 - INFO - [USING_CACHE][35, <code object main at 0x7fdbffc29030, file "example.py", line 28>]
#2019-12-06 00:08:21,179 - INFO - [FIRST_RUN][36, <code object main at 0x7fdbffc29030, file "example.py", line 28>]

```