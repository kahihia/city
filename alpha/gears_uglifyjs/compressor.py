import os
from gears.compressors import ExecCompressor


class UglifyJSCompressor(ExecCompressor):

    executable = 'nodejs'
    params = [os.path.join(os.path.dirname(__file__), 'compressor.js')]
