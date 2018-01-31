"""
Full test battery for skvz
"""

from skvzTestInstance import skvzTestInstance
from TestSuite import runTests,makeCombiName,makeLayerCombiName
import cfg
import itertools as it
from functools import reduce

def main():
    seqs = cfg.sequences
    in_names = cfg.class_sequence_names

    me = 'full' # 'hexbs'
    preset = 'ultrafast'#"veryslow"#"ultrafast"
    version = 4
    outname = "skvz_v{}_battery_{}_{}".format(version,preset,me)#"skvz_v{}_battery".format(version)

    bl_qps = (22, 27, 32, 37)#(7,12,17,22)
    el_qps = bl_qps#tuple(map(lambda x: x-5,bl_qps))
    el_snr_qps = tuple(map(lambda x: x-5,bl_qps))
    scal_qps = tuple(zip(bl_qps,el_qps))
    scal_snr_qps = tuple(zip(bl_qps,el_snr_qps))

    shared_param = ("--preset",preset,'--gop','0','--threads','3','--me',me)
    scal_param = ("--no-wpp",)
    no_tmvp = ("--no-tmvp",)
    tmvp = ("--tmvp",)

    bl2r_ref_frames = ('-r','2')
    el1r_ref_frames = ('-r','1')
    el2r_ref_frames = ('-r','2')
    scal1r_ref_frames = ('-r','1','--ilr','1')
    scal2r_ref_frames = ('-r','2','--ilr','1')

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
    REF2 = "2R" #Two ref
    REF1 = "1R" #One ref
    TMVP = "_TMVP" #Tmvp
    NOTMVP = ""

    single_layer_BL_param = [(reduce(lambda x,y: x + y[0], param, "BL"),) + reduce(lambda x,y: x + (y[1],), param, tuple())
                             for param in
                             it.product(
                                [(REF2,bl2r_ref_frames)], #Number of ref
                                [(SCALED,bl_scale),("",bl_snr_scale),(HSCALED,bl_halve_scale)], #Scale
                                [("",bl_qps)], #Qp
                                [("",tmvp)], #Use tmvp
                                )
                            ]

    single_layer_EL_param = [(reduce(lambda x,y: x + y[0], param, "EL"),) + reduce(lambda x,y: x + (y[1],), param, tuple())
                             for param in
                             it.product(
                                [(REF1,el1r_ref_frames),(REF2,el2r_ref_frames)], #Number of ref
                                [("",el_scale)], #Scale
                                [("",el_qps),(SNR,el_snr_qps)], #Qp
                                [(TMVP,tmvp),(NOTMVP,no_tmvp)], #Use tmvp
                                )
                            ]
    two_layer_param = [val for val in
                        ((reduce(lambda x,y: x + y[0], param, "SC"),) + reduce(lambda x,y: x + (y[1],), param, tuple())
                        for param in
                        it.product(
                            [(REF1,scal1r_ref_frames),(REF2,scal2r_ref_frames)], #Number of ref
                            [(SCAL,scal_scale),("1X",scal_snr_scale),(HSCAL,scal_halve_scale)], #Scale
                            [("",scal_qps),(SNR,scal_snr_qps)], #Qp
                            [(TMVP,tmvp),(NOTMVP,no_tmvp)], #Use tmvp
                        )
                      ) if (SNR in val[0] or SCAL in val[0] or HSCAL in val[0]) ]

    tests = []

    # Add BL/EL tests
    for (name, ref, scale, qp, tmvpp) in single_layer_BL_param + single_layer_EL_param:
        tests.append( skvzTestInstance(
            bin_name = cfg.skvz_ver_bin.format(version),
            inputs = seqs,
            input_names = in_names,
            test_name = name,
            qps = qp,
            layer_args = (shared_param + ref + tmvpp,),
            input_layer_scales = scale,
            ))
            
    # Add scalable tests
    for (name, ref, scale, qp, tmvpp) in two_layer_param:
        tests.append( skvzTestInstance(
            bin_name = cfg.skvz_ver_bin.format(version),
            inputs = seqs,
            input_names = in_names,
            test_name = name,
            qps = qp,
            layer_args = (shared_param + bl2r_ref_frames,
                          shared_param + scal_param + ref + tmvpp),
            input_layer_scales = scale,
            ))
    

    #Generate layer combi
    combi = [(bl[0],el[0],) for el in single_layer_EL_param for bl in single_layer_BL_param if (SCALED in bl[0] or HSCALED in bl[0] or SNR in el[0]) ]

    #Generate layers dict
    layers = { makeLayerCombiName(name) : ((-1,1) if (len(name) > 1) or ((name[0] not in [val[0] for val in single_layer_BL_param]) and (name[0] not in [val[0] for val in single_layer_EL_param])) else tuple())
              for name in [(val[0],) for val in single_layer_BL_param] + [(val[0],) for val in single_layer_EL_param] + [(val[0],) for val in two_layer_param] + combi}

    runTests(tests, outname,
             layers=layers,
             layer_combi=combi,
             s2_base=makeLayerCombiName(combi[3]))


if __name__ == "__main__":
    print("Execute test file " + __file__)
    main()