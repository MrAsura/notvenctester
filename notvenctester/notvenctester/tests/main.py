"""
Set test to run here
"""

#import test1
import scale_test1,shm_test1,preset_scal_test
import scal_test
import skvz_battery
import tmvp_merge_idx_test
import skvz_paper_tests
import perf_test

#test_list = [tmvp_merge_idx_test.main]
#test_list = [skvz_battery.main]
#test_list = [skvz_paper_tests.main]
#test_list = [scal_test.main]
#test_list = [test1.main]
#test_list = [scale_test1.main]#,
             #scal_test.main]#,
             #preset_scal_test.main,
             #shm_test1.main]
test_list = [perf_test.main]

def runTests():
    for test in test_list:
        test()

def addTest(test):
    global test_list
    test_list.append(test)