import configparser
import numpy as np

import output
import system
import waveforms


def read_config(fname):
    """Read configuration file
    :param fname: config file name
    :returns: ConfigParser containing configuration data
    :rtype: configparser.ConfigParser
    """
    config = configparser.ConfigParser()
    config.read(fname)
    return config


def generate_inputs(context, **kwargs):
    time = waveforms.time_array(1e-3, 10e-3, 1e-3)
    signal = waveforms.generate(kwargs.pop('waveform'), time, **kwargs)
    fname = kwargs['input'] if kwargs['input'] is not None else 'input.txt'
    np.savetxt(fname, signal, fmt='%d')
    output.success(f"Inputs saved on file {fname}")
