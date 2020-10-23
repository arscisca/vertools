import numpy as np
import scipy as sp


def time_array(tstart, tend, step):
    """Generate a time array
    :param tstart: first time instant
    :param tend: last time instant
    :param step: time step
    :type tstart: float
    :type tend: float
    :type step: float
    :returns: time array
    :rtype: numpy.ndarray
    """
    duration = tend - tstart
    nsamples = int(duration / step)
    time = np.arange(tstart, tend + step, step)
    # Chop extra elements introduced by float arithmetic
    time = time[:nsamples]
    return time


def generate(waveform, time, **kwargs):
    """Generate the requested waveform
    Args:
        waveform (str): waveform name
        time (numpy.ndarray): time array
        **kwargs: waveform-specific parameters
    Returns:
        numpy.ndarray
    """
    if waveform == 'constant':
        return constant(time, kwargs['value'])
    elif waveform == 'sine':
        return sine(time, kwargs['amplitude'], kwargs['frequency'], kwargs['phase'])
    elif waveform == 'step':
        return step(time, kwargs['t0'], kwargs['y0'], kwargs['y1'])

def sine(time, amplitude, frequency, phase):
    """Sine wave
    Args:
        time (numpy.ndarray): time array
        amplitude (int): sine wave amplitude
        frequency (float): sine wave frequency\
        phase (float): sine wave float (in radians)
    Returns:
        numpy.ndarray
    """
    return amplitude * np.sin(2 * np.pi * frequency * time + phase)


def step(time, t0, y0, y1):
    return np.array([y0 if t < t0 else y1 for t in time])


def constant(time, value):
    return np.full_like(time, value)