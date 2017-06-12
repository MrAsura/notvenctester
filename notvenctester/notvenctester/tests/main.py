"""
Set test to run here
"""

#import test1
import scale_test1,shm_test1
import scal_test

#test_list = [scal_test.main]
#test_list = [test1.main]
test_list = [scale_test1.main,
#             scal_test.main,
             shm_test1.main]

def runTests():
    for test in test_list:
        test()

def addTest(test):
    global test_list
    test_list.append(test)