"""
Test new functionality
"""

import cfg
from TestSuite import runTests
import TestUtils as TU
import re
import operator as op
from SummaryFactory import sn_BDBRM

def main():
    seqs = cfg.sequences[cfg.hevc_A] + cfg.sequences[cfg.hevc_B]
    in_names = cfg.class_sequence_names[cfg.hevc_A] + cfg.class_sequence_names[cfg.hevc_B]
    ver = 20
    shared_param = ("--preset", "ultrafast", "--gop", "0", "--no-tmvp")
    thread_range = (4,6,8,10,12,14)
    owf_range = (2,4,8,16)
    outname = "skvz_thread_owf_test_v{}".format(ver)

    # Set shared param
    tpg_scal = TU.TestParameterGroup()
    tpg_scal.add_const_param(version = ver,
                             bin_name = cfg.skvz_ver_bin.format(ver),
                             input_names = in_names,
                             layer_args = shared_param)\
             .add_param_set(_thrd = thread_range,
                            _owf = owf_range)
    tpg_sim = tpg_scal.copy()

    # Set scalable param
    round2 = lambda x,base=2: int(base * round(x / base))
    strscale = lambda size,scale: "x".join(map(lambda x: str(round2(int(x) * scale)),re.search("_*(\d+)x(\d+)[_.]*",size).group(1,2)))
    seq_scale = lambda scale, st: (st[0], strscale(st[1],scale), st[2])
    seq_map = lambda scale, seq: r"{}_{}_{}_zerophase_0.9pi.yuv".format(*seq_scale(scale,re.search("(.+\\\\.+)_(\d+x\d+)_(\d+)[_.]",seq).group(1,2,3)))
    bl_seq_map = lambda scale: lambda seq: (seq_map(scale[0], seq[0]),)
    scal_seq_map = lambda scale: lambda seq: (seq_map(scale[0],seq[0]),) + seq #TODO: Add scaling to el seq?

    scal_seqs = tuple(map(scal_seq_map((0.5,1)), seqs))


    tpg_scal.add_const_param(inputs = scal_seqs)
    
    tpg_scal.set_param_group_transformer(TU.transformerFactory(test_name = lambda *, _thrd, _owf, **param: "SCAL_THRD{}_OWF{}".format(_thrd, _owf),
                                                               layer_args = lambda *, layer_args, _thrd, _owf, **param: (layer_args + ("--threads",str(_thrd)) + ("--owf", str(_owf)), layer_args + ("--threads",str(_thrd)) + ("--owf", str(_owf)))))

    # Set simulcast param
    tpg_sim.add_const_param(inputs = seqs)\
            .add_param_set(_layer=("BL","EL"))

    tpg_sim.set_param_group_transformer(TU.transformerFactory(test_name = lambda *, _layer, _thrd, _owf, **param: "{}_THRD{}_OWF{}".format(_layer, _thrd, _owf),
                                                            layer_args = lambda *, layer_args, _thrd, _owf, **param: (layer_args + ("--threads",str(_thrd)) + ("--owf", str(_owf)),),
                                                            inputs = lambda *, inputs, _layer, **param: tuple(map(bl_seq_map((0.5,)), inputs)) if _layer in "BL" else inputs))


    #Run tests
    tests_scal = tpg_scal.to_skvz_test_instance()
    tests_sim = tpg_sim.to_skvz_test_instance()
    combi = TU.generate_combi(tpg_sim, combi_cond = TU.combiFactory(_thrd = op.eq,
                                                                    _owf = op.eq,
                                                                    _layer = lambda p1, p2: 0 if p1 == p2 else (-1 if p1 == "BL" else 1)))
    matrix_summary = TU.make_BDBRMatrix_definition(TU.get_test_names(tests_scal) + TU.get_combi_names(combi), write_bdbr = False, write_bits = False, write_psnr = False)

    summaries = {sn_BDBRM: matrix_summary}

    runTests(tests_scal + tests_sim, outname, layer_combi=combi, **summaries)

if __name__ == "__main__":
    print("Execute test file " + __file__)
    main()
