from TestInstance import TestInstance
import subprocess as sp
from multiprocessing.pool import Pool
import itertools as it
import re
import cfg
import hashlib

def _worker(seq,qp,cmd):
    p = sp.Popen(cmd,stdout=sp.PIPE,stderr=sp.PIPE)
    res = p.communicate()
    #if res[1] is not None:
        #print(seq,qp,res[1].decode())
    return (seq,qp,res[0].decode())

class shmTestInstance(TestInstance):
    """Test instance class for shm"""

    __CFG = r"-c"
    __BIN = r"-b"
    __INPUT = r"-i{lid}"
    __QP = r"-q{lid}"

    __sum_regex = r"SUMMARY\s-{56}\s"
    __i_slice_regex = r"I Slices\s*-{56}\s"
    __layer_regex_format = r"\sL{lid}\s+(\d+)\s+.\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)"
    __tot_stat_regex = r"Bytes written to file:\s+(\d+)\s+\((\d+\.\d+)\s+kbps\)\s+Total Time:\s+(\d+.\d+)\s+sec\."
    __num_layers_regex = r"Total number of layers\s+:\s+(\d+)"

    
    def __init__(self, test_name, configs, inputs = None, input_sizes = [()], input_names = None, layer_args = (), layer_sizes = [()], input_layer_scales = (), qps = (22, 27, 32, 37), out_name = 'out'):

        self._configs = configs
        self._inputs = inputs
        self._qps = qps
        self._layer_args = layer_args

        self._results = {}
        self._test_name = test_name

        self._out_name = out_name

        self._input_layer_scales = tuple([1 for i in range(len(configs[0]))])

        # Check that if input_names is given, it is the same length as configs. Both inputs and input_names must not be None
        if (input_names is not None and len(input_names) != len(configs)) or (inputs is not None and len(inputs) != len(configs)) or (input_names is None and inputs is None) :
            raise ValueError("Invalid input_names/inputs parameter given")

        self._input_names = {}
        for (conf,seq,name) in it.zip_longest(configs,inputs,input_names,fillvalue=None):
            if name is not None:
                self._input_names[name] = (conf,seq)
            else:
                self._input_names[str(seq)] = (conf,seq)

        #return super().__init__(test_name, inputs, input_sizes, layer_args, layer_sizes, input_layer_scales, qps, out_name)

    @staticmethod
    def _get_res_folder():
        return r"shm_res\\"


    def _get_fname_hash(self):
        hasher = hashlib.sha256()
        hasher.update(str(self._configs).encode())
        hasher.update(str(self._inputs).encode())
        hasher.update(str(self._qps).encode())
        hasher.update(str(self._layer_args).encode())
        return hasher.hexdigest()


    def _run_tests(self):
        runs = {}
        # Build commands
        for (name,(confs,seq)) in self._input_names.items():
            runs[name] = {}
            for qp in self._qps:
                cmd = [cfg.shm_bin]
                runs[name][qp] = cmd
                for conf in confs:
                    cmd.extend([self.__CFG,conf])
                cmd.extend([self.__BIN, cfg.results + self._out_name + "{qp}.hevc".format(qp=qp)])
                if seq is not None:
                    for lid in range(len(seq)):
                        cmd.extend([self.__INPUT.format(lid=lid),seq[lid]])
                        cmd.extend([self.__QP.format(lid=lid),str(qp)])
                cmd.extend(self._layer_args)

        seq_hash_tests_done = {} #Hold the number of test done for each sequence
        print_hash_format = "\t"
        hash_format = lambda seq: "seq{}".format(hash(seq))

        #Callback function for workers
        def cb( res ):
            nonlocal seq_hash_tests_done, self
            (seq,qp,val) = res
            # Update printout
            seq_hash_tests_done[hash_format(seq)] += 1
            print(print_hash_format.format(**seq_hash_tests_done),end='\r')
            # Save reuslts
            self._results[seq][qp] = val

        def cb_err( *args, **kwargs ):
            print("Error in worker") 

        pool = Pool(processes = 3)
        print("Start running {name} tests for sequences:".format(name=self._test_name))
        # Add test to pool and run in parallel
        line_sep = "\t|"
        for (seq,qps) in runs.items():
            seq_hash_tests_done[hash_format(seq)] = 0
            print_hash_format += "{" + hash_format(seq) + "}" + " of {}\t".format(len(qps.keys()))
            print(line_sep+seq)
            line_sep += "\t|"
            self._results[seq] = {}
            for (qp,cmd) in qps.items():
                pool.apply_async(_worker,(seq,qp,cmd),callback=cb,error_callback=cb_err)
        print(print_hash_format.format(**seq_hash_tests_done),end='\r')
        # Close pool and wait untill everythin is finnished
        pool.close()
        pool.join()
        print()
        print("Tests done.")


    """
    Parse kb/s from test results 
    """
    @staticmethod
    def __parseKBS(res,lres,nl,l_tot):
        vals = {}
        bit_rate = float(res.group(2))
        for lid in range(nl):
            if lres[lid]:
                lbits = lres[lid].group(2)
                vals[lid] = float(lbits)
            else:
                vals[lid] = bit_rate
        vals[l_tot] = bit_rate
        return vals

    """
    Parse kb from test results
    """
    @staticmethod
    def __parseKB(res,lkbs,nl,l_tot):
        vals = {}
        (bits,brate) = res.group(1,2)
        for lid in range(nl):
            vals[lid] = float(bits) * ( lkbs[lid] / float(brate) )
        vals[l_tot] = float(bits)
        return vals

    """
    Parse Time
    """
    @staticmethod
    def __parseTime(res,lres,nl,l_tot):
        vals = {}
        ttime = res.group(3)
        for lid in range(nl):
            if lres[lid]:
                ltime = ttime#lres[lid].group(6)
                vals[lid] = float(ltime)
            else:
                vals[lid] = float(ttime)
        vals[l_tot] = float(ttime)
        return vals

    """
    Parse psnr from test results
    """
    @staticmethod
    def __parsePSNR(lres,nl,l_tot):
        vals = {}
        vals[l_tot] = (0.0,0.0,0.0)
        for lid in range(nl):
            if lres[lid]:
                vals[lid] = tuple(map(float,lres[lid].group(3,4,5)))
                vals[l_tot] = tuple(map(lambda x,y: y+x/nl,vals[lid],vals[l_tot]))
            else:
                vals[lid] = (0.0,0.0,0.0)
        return vals

    """
    Parse needed values
    """
    @classmethod
    def __parseVals(cls,res,l_tot):
        trgt = {}
        sum_ex = re.search(cls.__sum_regex, str(res))
        i_ex = re.search(cls.__i_slice_regex, str(res))
        tot_ex = re.search(cls.__tot_stat_regex, str(res))
        lres_ex = {}
        num_layers = int(re.search(cls.__num_layers_regex,str(res)).group(1))
        layers = tuple(range(num_layers))
        for lid in layers:
            lres_ex[lid] = re.search(cls.__layer_regex_format.format(lid=lid), str(res))
        layers = layers + (l_tot,)
        kbs = cls.__parseKBS(tot_ex,lres_ex,num_layers,l_tot)
        kb = cls.__parseKB(tot_ex,kbs,num_layers,l_tot)
        time = cls.__parseTime(tot_ex,lres_ex,num_layers,l_tot)
        psnr = cls.__parsePSNR(lres_ex,num_layers,l_tot)
        return (kbs,kb,time,psnr,layers)
    
    def getResults(self, resBuildFunc, l_tot):
        results = {}
        for (seq,qps) in self._results.items():
            for (qp,res) in qps.items():
                (kbs,kb,time,psnr,lids) = type(self).__parseVals(res,l_tot)
                for lid in lids:
                    resBuildFunc(results,seq=seq,qp=qp,lid=lid,kbs=kbs[lid],kb=kb[lid],time=time[lid],psnr=psnr[lid])
        return results
