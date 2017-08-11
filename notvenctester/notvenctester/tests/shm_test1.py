"""
Scalable shm test
"""

from shmTestInstance import shmTestInstance
from TestSuite import runTests,makeCombiName,makeLayerCombiName
import cfg

def main():
    seqs = [(r"D:\stuff\Kimono1_960x540_24_zerophase_0.9pi.yuv",cfg.sequence_path+r"hevc-B\Kimono1_1920x1080_24.yuv"),
            (r"D:\stuff\Cactus_960x540_50_zerophase_0.9pi.yuv",cfg.sequence_path+r"hevc-B\Cactus_1920x1080_50.yuv")]
    const = (r"D:\stuff\encoder_my_scalable.cfg",r"D:\stuff\layers_no_mp.cfg")
    confs = [const + (r"D:\stuff\Kimono-2x.cfg",),
             const + (r"D:\stuff\Cactus-2x.cfg",)]
    confs_bl = [(r"D:\stuff\encoder_my_main.cfg",r"D:\stuff\Kimono_halve.cfg"),
                (r"D:\stuff\encoder_my_main.cfg",r"D:\stuff\Cactus_halve.cfg")]
    confs_el = [(r"D:\stuff\encoder_my_main.cfg",r"D:\stuff\Kimono.cfg"),
                (r"D:\stuff\encoder_my_main.cfg",r"D:\stuff\Cactus.cfg")]
    tests = []

    in_names = ["Kimono","Cactuar"]

    bl_qps = (22, 27, 32, 37)#(7,12,17,22) #(22, 27, 32, 37)
    el_qps = bl_qps#tuple(map(lambda x: x-5,bl_qps))

    tests.append( shmTestInstance(inputs = [(seq0,) for (seq0,seq1) in seqs],
                                  configs = confs_bl,
                                  input_names = in_names,
                                  qps = bl_qps,
                                  layer_args = ("-f",'5'),
                                  #input_layer_scales = (0.5,),
                                  test_name = "BL"
                                ))
    tests.append( shmTestInstance(inputs = [(seq1,) for (seq0,seq1) in seqs],
                                  configs = confs_el,
                                  input_names = in_names,
                                  qps = el_qps,
                                  layer_args = ("-f",'5'),
                                  #input_layer_scales = (1,),
                                  test_name = "EL"
                                ))
    tests.append( shmTestInstance(inputs = seqs,
                                  configs = confs,
                                  input_names = in_names,
                                  qps = el_qps,
                                  layer_args = ("-f",'5'),
                                  #layer_args = (("--preset","ultrafast","-n","5",'-r','1','--gop','0','--threads','0'),
                                  #              ('--preset','ultrafast','-n','5','-r','1','--gop','0','--threads','0')),
                                  #input_layer_scales = (0.5,1)
                                  test_name = "Scal"
                                ))

    runTests(tests,"shm_test_low_qp",
             layers={makeLayerCombiName(["BL","EL"]):(-1,),
                     "Scal":(-1,)},
             #combi=[("EL","BL")])#,
             layer_combi=[("BL","EL")])

if __name__ == "__main__":
    print("Execute test file " + __file__)
    main()