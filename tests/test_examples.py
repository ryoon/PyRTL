__author__ = 'John'

import glob
import os
import subprocess

import nose  # using the advanced features of nose to do this


"""
Tests all of the files in the example folder

Note that this file is structure dependent, so don't forget to change it if the
relative location of the examples changes
"""

def test_all_examples():
    x = __file__
    for file in glob.iglob(os.path.dirname(__file__) + "/../examples/*.py"):
        yield example_t, file


# note that this function cannot start with "test"
def example_t(file):
    print "testing file: " + file
    subprocess.check_call("python " + file)

