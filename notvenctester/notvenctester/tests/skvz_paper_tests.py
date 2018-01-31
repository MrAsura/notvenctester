"""
Skvz paper tests
"""

from skvzTestInstance import skvzTestInstance
from shmTestInstance import shmTestInstance
from TestSuite import runTests,makeCombiName,makeLayerCombiName
import cfg
import itertools as it
from functools import reduce

def main():
    plus_shm = True
    plus_threads = True

    #################_Define_skvz_tests_#################
    seqs = cfg.sequences[cfg.hevc_A] + cfg.sequences[cfg.hevc_B]
    in_names = cfg.class_sequence_names[cfg.hevc_A] + cfg.class_sequence_names[cfg.hevc_B]

    preset = 'ultrafast'#"veryslow"#"ultrafast"
    version = 5
    outname = "skvz_v{}_paper_{}{}{}".format(version,preset, "_shm" if plus_shm else "", "_thrds" if plus_threads else "")

    bl_snr_qps = (22, 27, 32, 37)#(26, 30, 34, 38) #SNR
    bl_spat_qps = (22, 27, 32, 37)#(22, 26, 30, 34) #Spatial

    #bl_qps = (22, 27, 32, 37)

    delta_snr_qp = (-5,)#(-4,-6) #SNR
    delta_spat_qp = (0,)#(0,2) #Spatial

    el_snr_qps = [tuple(map(lambda x: x+dqp, bl_snr_qps)) for dqp in delta_snr_qp]
    el_spat_qps = [tuple(map(lambda x: x+dqp, bl_spat_qps)) for dqp in delta_spat_qp]

    scal_snr_qps = [ tuple(zip(bl_snr_qps,el_qps)) for el_qps in el_snr_qps ]
    scal_spat_qps = [ tuple(zip(bl_spat_qps,el_qps)) for el_qps in el_spat_qps ]

    shared_param = ("--preset",preset,'--gop','0')

    thread_param = ('--threads','0','--owf','1','--wpp')
    no_thread_param = ('--threads','0','--owf','1','--no-wpp','--cpuid','0')

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
    THRD = "_THRD" #Use threads

    single_layer_BL_param = [val for val in 
                             ((reduce(lambda x,y: x + y[0], param, "BL"),) + reduce(lambda x,y: x + (y[1],), param, tuple())
                             for param in
                             it.product(
                                [(SCALED,bl_scale),("",bl_snr_scale),(HSCALED,bl_halve_scale)], #Scale
                                [(SNR,bl_snr_qps),("",bl_spat_qps)], #Qp
                                [("",no_thread_param),(THRD,thread_param)], #Threads
                                )
                             ) if (((SCALED in val[0] or HSCALED in val[0]) and not (SNR in val[0])) or (not (SCALED in val[0] or HSCALED in val[0]) and SNR in val[0]))
                            ]

    single_layer_EL_param = [(reduce(lambda x,y: x + y[0], param, "EL"),) + reduce(lambda x,y: x + (y[1],), param, tuple())
                             for param in
                             it.product(
                                [("",el_scale)], #Scale
                                #[(DQP1,el_spat_qps[0]),"""(DQP2,el_spat_qps[1]),"""(DQP1+SNR,el_snr_qps[0]),"""(DQP2+SNR,el_snr_qps[1])"""], #Qp
                                [(DQP1,el_spat_qps[0]), (DQP1+SNR,el_snr_qps[0]),], #Qp
                                [("",no_thread_param),(THRD,thread_param)], #Threads
                                )
                            ]
    two_layer_param = [val for val in
                        ((reduce(lambda x,y: x + y[0], param, "SC"),) + reduce(lambda x,y: x + (y[1],), param, tuple())
                        for param in
                        it.product(
                            [(SCAL,scal_scale),("1X",scal_snr_scale),(HSCAL,scal_halve_scale)], #Scale
                            #[(DQP1,scal_spat_qps[0]),"""(DQP2,scal_spat_qps[1]),"""(DQP1+SNR,scal_snr_qps[0]),"""(DQP2+SNR,scal_snr_qps[1])"""], #Qp
                            [(DQP1,scal_spat_qps[0]), (DQP1+SNR,scal_snr_qps[0]),], #Qp
                            [("",no_thread_param),("_THRD",thread_param)], #Threads
                        )
                      ) if (((SCAL in val[0] or HSCAL in val[0]) and not (SNR in val[0])) or (not (SCAL in val[0] or HSCAL in val[0]) and SNR in val[0])) ] #(SNR in val[0] or SCAL in val[0] or HSCAL in val[0]) ]

    tests = []

    # Add BL/EL tests
    for (name, scale, qp, thrd) in single_layer_BL_param + single_layer_EL_param:
        tests.append( skvzTestInstance(
            version = version,
            inputs = seqs,
            input_names = in_names,
            test_name = name,
            qps = qp,
            layer_args = (shared_param + ref_frames + thrd,),
            input_layer_scales = scale,
            ))
            
    # Add scalable tests
    for (name, scale, qp, thrd) in two_layer_param:
        tests.append( skvzTestInstance(
            version = version,
            inputs = seqs,
            input_names = in_names,
            test_name = name,
            qps = qp,
            layer_args = (shared_param + ref_frames + thrd,
                          shared_param + ref_frames + scal_ref_frames),
            input_layer_scales = scale,
            ))
    
    #################_Define_shm_tests_#################
    if plus_shm:

        shm_scal_2x_seqs = list(map(lambda x: (cfg.sequence_path+x[0],cfg.sequence_path+x[1]),
                                                               [(r"hevc-B\Kimono1_960x540_24_zerophase_0.9pi.yuv",cfg.sequences[cfg.Kimono1][0]),
                                                                (r"hevc-B\Cactus_960x540_50_zerophase_0.9pi.yuv",cfg.sequences[cfg.Cactus][0]),
                                                                (r"hevc-B\BasketballDrive_960x540_50_zerophase_0.9pi.yuv",cfg.sequences[cfg.BasketballDrive][0]),
                                                                (r"hevc-B\ParkScene_960x540_24_zerophase_0.9pi.yuv",cfg.sequences[cfg.ParkScene][0]),
                                                                (r"hevc-B\BQTerrace_960x540_60_zerophase_0.9pi.yuv",cfg.sequences[cfg.BQTerrace][0]),
                                                                (r"hevc-A\Traffic_1280x800_30_zerophase_0.9pi.yuv",cfg.sequences[cfg.Traffic][0]),                                                    
                                                                (r"hevc-A\PeopleOnStreet_1280x800_30_zerophase_0.9pi.yuv",cfg.sequences[cfg.PeopleOnStreet][0]),
                                                            ]))

        shm_scal_1_5x_seqs = list(map(lambda x: (cfg.sequence_path+x[0],cfg.sequence_path+x[1]),
                                                               [(r"hevc-B\Kimono1_1280x720_24_zerophase_0.9pi.yuv",cfg.sequences[cfg.Kimono1][0]),
                                                                (r"hevc-B\Cactus_1280x720_50_zerophase_0.9pi.yuv",cfg.sequences[cfg.Cactus][0]),
                                                                (r"hevc-B\BasketballDrive_1280x720_50_zerophase_0.9pi.yuv",cfg.sequences[cfg.BasketballDrive][0]),
                                                                (r"hevc-B\ParkScene_1280x720_24_zerophase_0.9pi.yuv",cfg.sequences[cfg.ParkScene][0]),
                                                                (r"hevc-B\BQTerrace_1280x720_60_zerophase_0.9pi.yuv",cfg.sequences[cfg.BQTerrace][0]),
                                                                (r"hevc-A\Traffic_1706x1066_30_zerophase_0.9pi.yuv",cfg.sequences[cfg.Traffic][0]),                                                    
                                                                (r"hevc-A\PeopleOnStreet_1706x1066_30_zerophase_0.9pi.yuv",cfg.sequences[cfg.PeopleOnStreet][0]),
                                                            ]))
    
        shm_snr_seqs = list(map(lambda x: (x[1],x[1]), shm_scal_2x_seqs))

        shm_bl_0_5x_seqs = list(map(lambda x: (x[0],), shm_scal_2x_seqs))
        shm_bl_0_7x_seqs = list(map(lambda x: (x[0],), shm_scal_1_5x_seqs))

        shm_el_seqs = list(map(lambda x: (x[1],), shm_snr_seqs))

        scal_consts = tuple(map(lambda x: cfg.shm_cfg+"paper_tests\\"+x, (r"encoder_1r_scalable.cfg",r"layers.cfg")))
        l_consts = tuple(map(lambda x: cfg.shm_cfg+"paper_tests\\"+x, (r"encoder_1r_main.cfg",)))
    
        scal_confs = list(map(lambda x: scal_consts + (cfg.shm_cfg+"paper_tests\\"+x,), [r"Kimono-2x.cfg",
                                                                                    r"Cactus-2x.cfg",
                                                                                    r"BasketballDrive-2x.cfg",
                                                                                    r"ParkScehe-2x.cfg",
                                                                                    r"BQTerrace-2x.cfg",
                                                                                    r"Traffic-2x.cfg",
                                                                                    r"PeopleOnStreet-2x.cfg",]
                                 ))

        hscal_confs = list(map(lambda x: scal_consts + (cfg.shm_cfg+"paper_tests\\"+x,), [r"Kimono-1.5x.cfg",
                                                                                    r"Cactus-1.5x.cfg",
                                                                                    r"BasketballDrive-1.5x.cfg",
                                                                                    r"ParkScehe-1.5x.cfg",
                                                                                    r"BQTerrace-1.5x.cfg",
                                                                                    r"Traffic-1.5x.cfg",
                                                                                    r"PeopleOnStreet-1.5x.cfg",]
                                 ))
    
        snr_confs = list(map(lambda x: scal_consts + (cfg.shm_cfg+"paper_tests\\"+x,), [r"Kimono-SNR.cfg",
                                                                                    r"Cactus-SNR.cfg",
                                                                                    r"BasketballDrive-SNR.cfg",
                                                                                    r"ParkScehe-SNR.cfg",
                                                                                    r"BQTerrace-SNR.cfg",
                                                                                    r"Traffic-SNR.cfg",
                                                                                    r"PeopleOnStreet-SNR.cfg",]
                                 ))

        bl_0_5x_confs = list(map(lambda x: l_consts + (cfg.shm_cfg+"paper_tests\\"+x,), [r"Kimono-0.5x.cfg",
                                                                                    r"Cactus-0.5x.cfg",
                                                                                    r"BasketballDrive-0.5x.cfg",
                                                                                    r"ParkScehe-0.5x.cfg",
                                                                                    r"BQTerrace-0.5x.cfg",
                                                                                    r"Traffic-0.5x.cfg",
                                                                                    r"PeopleOnStreet-0.5x.cfg",]
                                 ))

        bl_0_7x_confs = list(map(lambda x: l_consts + (cfg.shm_cfg+"paper_tests\\"+x,), [r"Kimono-0.7x.cfg",
                                                                                    r"Cactus-0.7x.cfg",
                                                                                    r"BasketballDrive-0.7x.cfg",
                                                                                    r"ParkScehe-0.7x.cfg",
                                                                                    r"BQTerrace-0.7x.cfg",
                                                                                    r"Traffic-0.7x.cfg",
                                                                                    r"PeopleOnStreet-0.7x.cfg",]
                                 ))

        el_confs = list(map(lambda x: l_consts + (cfg.shm_cfg+"paper_tests\\"+x,), [r"Kimono.cfg",
                                                                                    r"Cactus.cfg",
                                                                                    r"BasketballDrive.cfg",
                                                                                    r"ParkScehe.cfg",
                                                                                    r"BQTerrace.cfg",
                                                                                    r"Traffic.cfg",
                                                                                    r"PeopleOnStreet.cfg",]
                                 ))

        shm_in_names = list(map(lambda x: cfg.class_sequence_names[x], [cfg.Kimono1,
                                                                        cfg.Cactus,
                                                                        cfg.BasketballDrive,
                                                                        cfg.ParkScene,
                                                                        cfg.BQTerrace,
                                                                        cfg.Traffic,
                                                                        cfg.PeopleOnStreet,]
                                ))


        shm_BL_param = [val for val in 
                                 ((reduce(lambda x,y: x + y[0], param, "SHM_BL"),) + reduce(lambda x,y: x + y[1], param, tuple())
                                 for param in
                                 it.product(
                                    [(SCALED,(shm_bl_0_5x_seqs,bl_0_5x_confs,bl_spat_qps)),(HSCALED,(shm_bl_0_7x_seqs,bl_0_7x_confs,bl_spat_qps)),(SNR,(shm_el_seqs,el_confs,bl_snr_qps)),], #inputs + scales + qp
                                    )
                                 ) if (((SCALED in val[0] or HSCALED in val[0]) and not (SNR in val[0])) or (not (SCALED in val[0] or HSCALED in val[0]) and SNR in val[0]))
                                ]

        shm_EL_param = [(reduce(lambda x,y: x + y[0], param, "SHM_EL"),) + reduce(lambda x,y: x + (y[1],), param, tuple())
                                 for param in
                                 it.product(
                                    [("1X",shm_el_seqs),], #inputs
                                    [("",el_confs),], #Scale confs
                                    [("",el_spat_qps[0]), (SNR,el_snr_qps[0]),], #Qp
                                    )
                                ]

        shm_param = [val for val in
                        ((reduce(lambda x,y: x + y[0], param, "SHM"),) + reduce(lambda x,y: x + y[1], param, tuple())
                        for param in
                        it.product(
                            [(SCAL,(shm_scal_2x_seqs,scal_confs,scal_spat_qps[0])),(HSCAL,(shm_scal_1_5x_seqs,hscal_confs,scal_spat_qps[0])),(SNR,(shm_snr_seqs,snr_confs,scal_spat_qps[0])),], #inputs + confs + qp
                        )
                      ) if  ((SCAL in val[0] and not HSCAL in val[0] and not SNR in val[0]) or (not SCAL in val[0] and HSCAL in val[0] and not SNR in val[0]) or (not SCAL in val[0] and not HSCAL in val[0] and SNR in val[0]))
                    ]
        
        for (name, inputs, confs, qps) in shm_param + shm_BL_param + shm_EL_param:
            tests.append( shmTestInstance(inputs = inputs,
                                          configs = confs,
                                          input_names = shm_in_names,
                                          qps = qps,
                                          #layer_args = ("-f",'5'),
                                          #input_layer_scales = (0.5,),
                                          test_name = name
                                        ))

    #################_Define_run_tests_parameters_#################
    #Generate layer combi
    combi = [(bl[0],el[0],) for el in single_layer_EL_param for bl in single_layer_BL_param if (((SCALED in bl[0] or HSCALED in bl[0]) and not (SNR in el[0])) or (not (SCALED in bl[0] or HSCALED in bl[0]) and SNR in el[0])) and ((THRD in bl[0]) == (THRD in el[0]))] #(SCALED in bl[0] or HSCALED in bl[0] or SNR in el[0]) ]
    combi += [(bl[0],el[0],) for el in shm_EL_param for bl in shm_BL_param if (((SCALED in bl[0] or HSCALED in bl[0]) and not (SNR in el[0])) or (not (SCALED in bl[0] or HSCALED in bl[0]) and SNR in el[0]))]

    #Generate layers dict
    layers = { makeLayerCombiName(name) : ((-1,1) if (len(name) > 1) or ((name[0] not in [val[0] for val in single_layer_BL_param]) and (name[0] not in [val[0] for val in single_layer_EL_param]) and (name[0] not in [val[0] for val in shm_BL_param]) and (name[0] not in [val[0] for val in shm_EL_param])) else tuple())
              for name in [(val[0],) for val in single_layer_BL_param] + [(val[0],) for val in single_layer_EL_param] + [(val[0],) for val in two_layer_param] + [(val[0],) for val in shm_param] + [(val[0],) for val in shm_BL_param] + [(val[0],) for val in shm_EL_param] + combi}

    runTests(tests, outname,
             layers=layers,
             layer_combi=combi)


    

if __name__ == "__main__":
    print("Execute test file " + __file__)
    main()