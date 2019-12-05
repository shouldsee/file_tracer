#!/usr/bin/env python
#from setuptools import setup
from distutils.core import setup
#import setuptools
import os,glob,sys
setup(
	name='FileTracer',
	version='0.0.1',
    packages=['.',],
	include_package_data=True,
	license='MIT',
	author='Feng Geng',
	author_email='shouldsee.gem@gmail.com',
	long_description=open('README.md').read(),
	install_requires=[
		x.strip() for x in open("requirements.txt","r")
        	if x.strip() and not x.strip().startswith("#")
	],

)


