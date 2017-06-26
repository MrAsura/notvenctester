"""
Scalable test
"""

from skvzTestInstance import skvzTestInstance
from TestSuite import runTests,makeCombiName,makeLayerCombiName


def main():
    seqs = [(r"hevc-B\Kimono1_1920x1080_24.yuv",),
            (r"hevc-B\Cactus_1920x1080_50.yuv",)]
    tests = []

    in_names = ["Kimono","Cactuar"]

    bl_qps = (7,12,17,22)#(22, 27, 32, 37)
    el_qps = tuple(map(lambda x: x-5,bl_qps))

    tests.append( skvzTestInstance(inputs = seqs,
                        test_name = "BL",
                        input_names = in_names,
                        qps = bl_qps,
                        layer_args = (("--preset","ultrafast","-n","5",'-r','1','--gop','0','--threads','3','--no-wpp'),),
                        input_layer_scales = (0.5,)
                        ))
    tests.append( skvzTestInstance(inputs = seqs,
                        test_name = "EL",
                        input_names = in_names,
                        qps = bl_qps,
                        layer_args = (("--preset","ultrafast","-n","5",'-r','1','--gop','0','--threads','3','--no-wpp'),),
                        input_layer_scales = (1,)
                        ))
    tests.append( skvzTestInstance(inputs = seqs,
                        test_name = "Scal",
                        input_names = in_names,
                        qps = bl_qps,#tuple(zip(bl_qps,el_qps)),
                        layer_args = (("--preset","ultrafast","-n","5",'-r','1','--gop','0'),
                                      ('--preset','ultrafast','-n','5','-r','0','--ilr','1','--gop','0','--threads','3','--no-wpp')),
                        input_layer_scales = (0.5,1)
                        ))

    runTests(tests,"scale_test_low_qp",
             layers={makeLayerCombiName(["BL","EL"]):(-1,),
                     "Scal":(-1,0,1)},
#             combi=[("EL","BL")],
             layer_combi=[("BL","EL")])

