import numpy as np

import output
import system
import waveforms


def generate_inputs(context):
    signal = waveforms.generate(context)
    fname = context.get('Input', 'file', fallback='inputs.txt')
    np.savetxt(fname, signal, fmt='%d')
    output.success(f"Inputs saved on file {fname}")
