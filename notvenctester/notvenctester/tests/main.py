"""
Set test to run here
"""

#import test1
import scale_test1,shm_test1,preset_scal_test
import scal_test
import skvz_v3_battery

test_list = [skvz_v3_battery.main]
#test_list = [scal_test.main]
#test_list = [test1.main]
#test_list = [scale_test1.main]#,
             #scal_test.main]#,
             #preset_scal_test.main,
             #shm_test1.main]

def runTests():
    for test in test_list:
        test()

def addTest(test):
    global test_list
    test_list.append(test)