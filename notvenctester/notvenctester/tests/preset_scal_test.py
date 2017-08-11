"""
Scalable test for presets
"""

from skvzTestInstance import skvzTestInstance
from TestSuite import runTests,makeCombiName,makeLayerCombiName


def main():
    seqs = [(r"hevc-B\Kimono1_1920x1080_24.yuv",),
            (r"hevc-B\Cactus_1920x1080_50.yuv",)]
    tests = []

    in_names = ["Kimono","Cactuar"]

    bl_qps = (22, 27, 32, 37)
    el_qps = tuple(map(lambda x: x-5,bl_qps))

    # Ultra fast
    tests.append( skvzTestInstance(inputs = seqs,
                        test_name = "BL_UF",
                        input_names = in_names,
                        #qps = bl_qps,
                        layer_args = (("--preset","ultrafast","-n","5",'-r','1','--gop','0','--threads','3','--no-wpp'),),
                        input_layer_scales = (0.5,)
                        ))
    tests.append( skvzTestInstance(inputs = seqs,
                        test_name = "EL_UF",
                        input_names = in_names,
                        #qps = el_qps,
                        layer_args = (("--preset","ultrafast","-n","5",'-r','1','--gop','0','--threads','3','--no-wpp'),),
                        input_layer_scales = (1,)
                        ))
    tests.append( skvzTestInstance(inputs = seqs,
                        test_name = "Scal_UF",
                        input_names = in_names,
                        #qps = tuple(zip(bl_qps,el_qps)),
                        layer_args = (("--preset","ultrafast","-n","5",'-r','1','--gop','0'),
                                      ('--preset','ultrafast','-n','5','-r','0','--ilr','1','--gop','0','--threads','3','--no-wpp')),
                        input_layer_scales = (0.5,1)
                        ))

    # Ultra slow
    tests.append( skvzTestInstance(inputs = seqs,
                        test_name = "BL_VS",
                        input_names = in_names,
                        #qps = bl_qps,
                        layer_args = (("--preset","veryslow","-n","5",'-r','1','--gop','0','--threads','3','--no-wpp'),),
                        input_layer_scales = (0.5,)
                        ))
    tests.append( skvzTestInstance(inputs = seqs,
                        test_name = "EL_VS",
                        input_names = in_names,
                        #qps = el_qps,
                        layer_args = (("--preset","veryslow","-n","5",'-r','1','--gop','0','--threads','3','--no-wpp'),),
                        input_layer_scales = (1,)
                        ))
    tests.append( skvzTestInstance(inputs = seqs,
                        test_name = "Scal_VS",
                        input_names = in_names,
                        #qps = tuple(zip(bl_qps,el_qps)),
                        layer_args = (("--preset","veryslow","-n","5",'-r','1','--gop','0'),
                                      ('--preset','veryslow','-n','5','-r','0','--ilr','1','--gop','0','--threads','3','--no-wpp')),
                        input_layer_scales = (0.5,1)
                        ))

    runTests(tests,"preset_scale_test",
             layers={makeLayerCombiName(["BL_UF","EL_UF"]):(-1,),
                     makeLayerCombiName(["BL_VS","EL_VS"]):(-1,),
                     "Scal_UF":(-1,),
                     "Scal_VS":(-1,)},
             layer_combi=[("BL_VS","EL_VS"),
                          ("BL_UF","EL_UF")])

