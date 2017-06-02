"""
Beta test
"""

from ..skvzTestInstance import skvzTestInstance
from ..TestSuite import runTests,makeCombiName


def main():
    seqs = [(r"hevc-B\Kimono1_1920x1080_24.yuv",),
            (r"hevc-B\Cactus_1920x1080_50.yuv",)]
    tests = []

    tests.append( skvzTestInstance(inputs = seqs,
                        test_name = "Test1",
                        layer_args = (("--preset","ultrafast","-n","5",'-r','1'),),
                        input_layer_scales = (0.5,)
                        ))
    tests.append( skvzTestInstance(inputs = seqs,
                        test_name = "Test2",
                        layer_args = (("--preset","ultrafast","-n","5",'-r','1'),),
                        input_layer_scales = (1,)
                        ))
    tests.append( skvzTestInstance(inputs = seqs,
                        test_name = "Test3",
                        layer_args = (("--preset","ultrafast","-n","5",'-r','1','--gop','0','--threads','0'),('--preset','ultrafast','--gop','0','-n','5','-r','1','--threads','0')),
                        input_layer_scales = (1,1)
                        ))
    tests.append( skvzTestInstance(inputs = seqs,
                        test_name = "Test4",
                        layer_args = (("--preset","ultrafast","-n","5",'-r','1','--gop','0','--threads','0'),('--preset','ultrafast','--gop','0','-n','5','-r','1','--threads','0')),
                        input_layer_scales = (0.5,1)
                        ))
    runTests(tests,"Test1",
             layers={"Test2":(-1,),"Test3":(0,),makeCombiName(("Test1","Test2","Test2")):()},
             combi=[("Test1","Test2"),("Test1","Test1"),("Test2","Test1"),("Test2","Test2"),("Test1","Test2","Test2")])

