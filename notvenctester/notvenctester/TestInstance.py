import subprocess as sp
import itertools as it
import re
import cfg

class TestInstance(object):
    
    __LAYER = "--layer"
    __LAYER_RES = "--layer-res"
    __QP = "--qp"
    __INPUT = "--input"
    __INPUT_RES = "--input-res"
    __OUTPUT = "--output"
    __DEBUG = "--debug"

    """
    Create a test instance object
    @param inputs: Specify input files for each input. Can be a list of input sets for several sequences. Same parameter will be used for each input set.
    @param input_sizes: Specify sizes for each input (if not in filename)
    @param layer_args: Specify parameters not give as separate args (iterable with an element for each layer)
    @param layer_sizes: Specify layer sizes (iterable with an element for each layer). Gets overwriten if scales is given
    @param input_layer_scales: Set layer Sizes as input sizes scaled by given values
    @param qps: Qp values for which the test is run
    @param test_name: A name for the test instance
    @param out_name: Name for the output files
    @return self object
    """
    def __init__(self, test_name, inputs, input_sizes=[()], layer_args=(), layer_sizes=[()], input_layer_scales=(), qps=(22, 27, 32, 37), out_name="out"):
        self._layer_sizes = layer_sizes
        self._layer_args = layer_args
        self._inputs = inputs
        self._input_sizes = input_sizes
        self._input_layer_scales = input_layer_scales

        self._qps = qps
        self._num_layers = max(len(layer_sizes),len(layer_args))
        
        self._test_name = test_name
        if not test_name:
            self._test_name = inputs[0]

        self._out_name = out_name

        if input_layer_scales:
            round2 = lambda x,base=2: int(base*round(x/base))
            strscale = lambda size,scale: "x".join(map(lambda x: str(round2(int(x)*scale)),re.search("_*(\d+)x(\d+)[_.]*",size).group(1,2)))
            self._layer_sizes = []
            for (input_set,input_set_sizes) in it.zip_longest(inputs,input_sizes,fillvalue=tuple()):
                insizes = input_set_sizes
                fval = 1
                if not input_set_sizes:
                    #Get sizes from the given inputs
                    insizes = input_set
                    fval = input_set[-1] if len(input_set) < len(input_layer_scales) else 1
                else:
                    fval =  input_set_sizes[-1] if len(input_set) < len(input_layer_scales) else 1
                self._layer_sizes.append( tuple( strscale(size,scale) for (scale,size) in it.zip_longest(input_layer_scales,insizes,fillvalue = fval) ) )
        
        #Will contain the execution results
        self._results = {}

        #return self

    def run(self):
        runs = {}
        for (seqs,sizes) in zip(self._inputs,self._layer_sizes):
            seq_runs = {}
            for qp in self._qps:
                cmd = [cfg.skvz_bin]
                for (l,l_res,l_arg) in it.zip_longest([None] + [self.__LAYER] * (self._num_layers - 1),sizes,self._layer_args,fillvalue=None):
                    if l is not None:
                        cmd.append(l)
                    if l_arg is not None:
                        cmd.extend(l_arg)
                    if l_res is not None:
                        cmd.extend([self.__LAYER_RES,l_res])
                    cmd.extend([self.__QP,str(qp)])
                        
                    for input in seqs:
                        cmd.extend([self.__INPUT,cfg.sequence_path + input])
                        
                cmd.extend([self.__OUTPUT, cfg.results + self._out_name + "_{qp}.hevc".format(qp=qp)])    
                seq_runs[qp] = cmd
            runs[str(seqs)] = seq_runs
   
        print("Running test {}".format(self._test_name))
        for (seq,qps) in runs.items():
            print("  Sequence: {}".format(seq))
            self._results[seq] = {}
            i = 0
            print("    {} of {} runs complete.\r".format(i,len(qps.keys())),end='')
            for (qp,cmd) in qps.items():
                #print(cmd)
                p = sp.Popen(cmd,stdout=None,stderr=sp.PIPE)
                out = p.communicate()
                #print("_________________________out_____________________")
                #print(out)
                self._results[seq][qp] = out[1]
                i = i + 1
                print("    {} of {} runs complete.\r".format(i,len(qps.keys())),end='')
            print("")
        
        




