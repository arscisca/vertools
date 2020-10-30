import numpy as np
import scipy as sp
import scipy.signal


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


def generate(context):
    """Generate the requested waveform
    Args:
        context (vertools.context.Context): context variable
    Returns:
        numpy.ndarray
    """
    waveform = context.get('CommandLine', 'waveform')
    tstart = context.get('Input', 'tstart')
    tend = context.get('Input', 'tend')
    tstep = context.get('Input', 'tstep')
    time = time_array(tstart, tend, tstep)
    if waveform == 'constant':
        return constant(time, context.get('CommandLine', 'value'))
    elif waveform == 'step':
        return step(time, context.get('CommandLine', 't0'), context.get('CommandLine', 'y0'),
                    context.get('CommandLine', 'y1'))
    elif waveform == 'sine':
        return sine(time, context.get('CommandLine', 'amplitude'), context.get('CommandLine', 'frequency'),
                    context.get('CommandLine', 'phase'))
    elif waveform == 'chirp':
        return chirp(time, context.get('CommandLine', 'amplitude'), context.get('CommandLine', 'duration'),
                     context.get('CommandLine', 'f0'), context.get('CommandLine', 'f1'),
                     context.get('CommandLine', 'method', fallback='linear'))


def constant(time, value):
    """Constant function
    Args:
        time (numpy.ndarray): time array
        value (int): constant value
    Returns:
        numpy.ndarray
    """
    return np.full_like(time, value)


def step(time, t0, y0, y1):
    """Step function
    Args:
        time (numpy.ndarray): time array
        t0 (float): time instant of the step
        y0 (int): initial value of the step
        y1 (int): final value of the step
    Returns:
        numpy.ndarray
    """
    return np.array([y0 if t < t0 else y1 for t in time])


def sine(time, amplitude, frequency, phase):
    """Sine wave
    Args:
        time (numpy.ndarray): time array
        amplitude (int): sine wave amplitude
        frequency (float): sine wave frequency
        phase (float): sine wave float (in radians)
    Returns:
        numpy.ndarray
    """
    return amplitude * np.sin(2 * np.pi * frequency * time + phase)


def chirp(time, amplitude, duration, f0, f1, method):
    """Chirp signal
    Args:
        time (numpy.ndarray): time array
        amplitude (int): signal amplitude
        duration (float): chirp duration
        f0 (float): initial frequency
        f1 (float): final frequency
        method (str): chirp method
    Returns:
        numpy.ndarray
    """
    return amplitude * sp.signal.chirp(time, f0, duration, f1, method)
