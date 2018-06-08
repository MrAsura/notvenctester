"""
Performance tests between versions
"""

from skvzTestInstance import skvzTestInstance
from shmTestInstance import shmTestInstance
from TestSuite import runTests,makeCombiName,makeLayerCombiName
import cfg
import itertools as it
from functools import reduce
import re

def main():
    plus_shm = True
    plus_threads = True

    #################_Define_skvz_tests_#################
    seqs = cfg.sequences[cfg.hevc_A] + cfg.sequences[cfg.hevc_B]
    in_names = cfg.class_sequence_names[cfg.hevc_A] + cfg.class_sequence_names[cfg.hevc_B]

    preset = 'ultrafast'#'veryslow'#'ultrafast'#"veryslow"#"ultrafast"
    versions = [5, 6];
    outname = "skvz_v{}_perf_test".format(6)

    bl_snr_qps = (22, 27, 32, 37)#(26, 30, 34, 38) #SNR
    bl_spat_qps = (22, 27, 32, 37)#(22, 26, 30, 34) #Spatial

    #bl_qps = (22, 27, 32, 37)

    delta_snr_qp = (-5,)#(-4,-6) #SNR
    delta_spat_qp = (0,)#(0,2) #Spatial

    dqps = (1,2,3,4,5,6,7,8,9,10)

    el_snr_qps = [tuple(map(lambda x: x+dqp, bl_snr_qps)) for dqp in delta_snr_qp]
    el_spat_qps = [tuple(map(lambda x: x+dqp, bl_spat_qps)) for dqp in delta_spat_qp]

    scal_snr_qps = [ tuple(zip(bl_snr_qps,el_qps)) for el_qps in el_snr_qps ]
    scal_spat_qps = [ tuple(zip(bl_spat_qps,el_qps)) for el_qps in el_spat_qps ]

    shared_param = ("--preset",preset,'--gop','0')

    thread_param = ('--threads','auto','--owf','auto','--wpp')
    no_thread_param = ('--threads','0','--owf','1','--no-wpp','--cpuid','0')

    tmvp =('--tmvp')
    no_tmvp = ('--no-tmvp')

    in_layer_0 = ('--input-layer','0')
    in_layer_1 = ('--input-layer','1')

    ref_frames = ('-r','1')
    scal_ref_frames = ('--ilr','1')

    bl_scale = (0.5,)
    bl_snr_scale = (1,)
    el_scale = (1,)
    scal_scale = bl_scale + el_scale
    scal_snr_scale = bl_snr_scale + el_scale
    bl_halve_scale = (1/1.5,)
    scal_halve_scale = bl_halve_scale + el_scale

    SNR = "_SNR" #Spatial scalability not used
    SCALED = "0.5X" #Downscaled by 0.5
    HSCALED = "0.7X" #Downscaled by 1/1.5
    SCAL = "2X" # 2x scalability
    HSCAL = "1.5X" # 1.5x scalability
    DQP1 = ""#"_DQP1" # First delta qp used
    DQP2 = "_DQP2" # Second delta qp used
    DQP = r"_DQP{}"
    THRD = "_THRD" #Use threads
    VER = "_v{}" #version

    round2 = lambda x,base=2: int(base*round(x/base))
    strscale = lambda size,scale: "x".join(map(lambda x: str(round2(int(x)*scale)),re.search("_*(\d+)x(\d+)[_.]*",size).group(1,2)))
    seq_scale = lambda scale, st: (st[0], strscale(st[1],scale), st[2])
    seq_map = lambda scale, seq: r"{}_{}_{}_zerophase_0.9pi.yuv".format( *seq_scale(scale,re.search("(.+\\\\.+)_(\d+x\d+)_(\d+)[_.]",seq).group(1,2,3)) )
    bl_seq_map = lambda scale: lambda seq: (seq_map(scale[0], seq[0]),)
    scal_seq_map = lambda scale: lambda seq: (seq_map(scale[0],seq[0]), ) + seq #TODO: Add scaling to el seq?

    
    two_layer_param = [val for val in
                        ((reduce(lambda x,y: x + y[0], param, "SC"),) + reduce(lambda x,y: x + y[1], param, tuple())
                        for param in
                        it.product(
                            [(SCAL,((1,1),tuple(map(scal_seq_map(scal_scale),seqs)))),("1X",(scal_snr_scale,seqs)),], #Scale
                            [(DQP1,(scal_spat_qps[0],)), (DQP1+SNR,(scal_snr_qps[0],)),], #Qp
                            [(THRD,(thread_param,)),],#[("",(tuple(),))]#[("",(no_thread_param,)),("_THRD",(thread_param,))], #Threads
                            [(VER.format(ver),((cfg.skvz_ver_bin.format(ver),ver),)) for ver in versions], #versions
                        )
                      ) if ((SCAL in val[0] and not (SNR in val[0])) or (not (SCAL in val[0]) and SNR in val[0]))
                      ]


    tests = []

    
            
    # Add scalable tests
    for (name, scale, input, qp, thrd, ver) in two_layer_param:
        tests.append( skvzTestInstance(
            version = ver[1],
            inputs = input,
            input_names = in_names,
            test_name = name,
            qps = qp,
            layer_args = (shared_param + ref_frames + thrd,
                          shared_param + ref_frames + scal_ref_frames + thrd),
            input_layer_scales = scale,
            bin_name = ver[0],
            ))
    
    
    #################_Define_run_tests_parameters_#################
    
    runTests(tests, outname,
             input_res = True,
             )


    

if __name__ == "__main__":
    print("Execute test file " + __file__)
    main()