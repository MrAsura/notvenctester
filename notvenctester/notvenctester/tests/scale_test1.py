"""
Scalable test
"""

from TestInstance import TestInstance
from TestSuite import runTests,makeCombiName,makeLayerCombiName


def main():
    seqs = [(r"hevc-B\Kimono1_1920x1080_24.yuv",),
            (r"hevc-B\Cactus_1920x1080_50.yuv",)]
    tests = []

    tests.append( TestInstance(inputs = seqs,
                        test_name = "BL",
                        layer_args = (("--preset","ultrafast","-n","5",'-r','1'),),
                        input_layer_scales = (0.5,)
                        ))
    tests.append( TestInstance(inputs = seqs,
                        test_name = "EL",
                        layer_args = (("--preset","ultrafast","-n","5",'-r','1'),),
                        input_layer_scales = (1,)
                        ))
    tests.append( TestInstance(inputs = seqs,
                        test_name = "Scal",
                        layer_args = (("--preset","ultrafast","-n","5",'-r','1','--gop','0','--threads','0'),
                                      ('--preset','ultrafast','-n','5','-r','1','--gop','0','--threads','0')),
                        input_layer_scales = (0.5,1)
                        ))

    runTests(tests,"scale_test2",
             layers={makeLayerCombiName(["BL","EL"]):(-1,)},
             combi=[("EL","BL")],
             layer_combi=[("BL","EL")])

