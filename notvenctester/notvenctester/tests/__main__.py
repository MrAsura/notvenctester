"""
Run all tests in test set or ones given as a parameter
"""

import sys
#from __init__ import test_set

import test_new_functionality
test_set = {
#    "perf_test": perf_test.main,
#    "tmvp_merge_idx_test": tmvp_merge_idx_test.main,
#    "skvz_battery": skvz_battery.main,
#    "skvz_paper_tests": skvz_paper_tests.main,
#    "scal_test": scal_test.main,
#    "test1": test1.main,
#    "scale_test1": scale_test1.main,
#    "scal_test": scal_test.main,
#    "preset_scal_test": preset_scal_test.main,
#    "shm_test1": shm_test1.main,
    "test_new": test_new_functionality.main
    }

if len(sys.argv) > 1:
    for name in sys.argv[1:]:
        print("Running test {}".format(name))
        test_set[name]()
else:
    for (name,func) in test_set.items():
        print("Running test {}".format(name))
        func()
    