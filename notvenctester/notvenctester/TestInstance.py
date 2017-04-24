class TestInstance(object):
    """
    Create a test instance object
    @param layer_args: Specify parameters not give as separate args (iterable with an element for each layer)
    @param layer_sizes: Specify layer sizes (iterable with an element for each layer)
    @param inputs: Specify input files for each input
    @param input_sizes: Specify sizes for each input (if not in filename)
    @return self object
    """
    def __init__(self, layer_args, layer_sizes, inputs, input_sizes, *args, **kwargs):
        self._layer_sizes = layer_sizes
        self._layer_args = layer_args
        self._inputs = inputs
        self._input_sizes = input_sizes
        return self




