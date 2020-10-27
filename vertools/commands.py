import numpy as np

import output
import system
import waveforms


def generate_inputs(args, context):
    context.set('CommandLine', 'waveform', args.waveform)
    signal = waveforms.generate(context)
    fname = context.get('Input', 'file', fallback='inputs.txt')
    np.savetxt(fname, signal, fmt='%d')
    output.success(f"Inputs saved on file {fname}")


def simulate(args, context):
    script = context.get('Simulation', 'script')
    output.status(f"Launching simulation script ({script})")
    if context.get('Simulation', 'disable_log') is True:
        system.launch_script(script, stdout=False, stderr=False)
    else:
        logfile = context.get('Simulation', 'log')
        with open(logfile, 'w') as log:
            system.launch_script(script, stdout=log, stderr=log)
        output.update(f"Simulation log saved in {logfile}", 2)
    output.success('Done!')

