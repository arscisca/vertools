import os
import numpy as np

import output
import system
import waveforms


def clean(args, context):
    """Remove validation files
    Args:
        args (argparse.NameSpace): namespace from command line parsing
        context (vertools.Context): context
    """
    # Files to be removed
    targets = {
        'Simulation': ['results', 'log']
    }
    output.status('Cleaning files')
    for section, files in targets.items():
        for file in files:
            fname = context.get(section, file)
            try:
                os.remove(fname)
                output.update(f"Removed {fname}", 2)
            except OSError:
                # Ignore missing files
                pass
    output.success("Done")


def generate_inputs(args, context):
    """Generate input file
    Args:
        args (argparse.NameSpace): namespace from command line parsing
        context (vertools.Context): context
    """
    context.set('CommandLine', 'waveform', args.waveform)
    signal = waveforms.generate(context)
    fname = context.get('Input', 'file', fallback='inputs.txt')
    np.savetxt(fname, signal, fmt='%d')
    output.success(f"Inputs saved on file {fname}")


def simulate(args, context):
    """Run simulation script
    Args:
        args (argparse.NameSpace): namespace from command line parsing
        context (vertools.Context): context
    """
    script = context.get('Simulation', 'script')
    output.status(f"Launching simulation script ({script})")
    if context.get('Simulation', 'disable_log') is True:
        system.launch_script(script, stdout=False, stderr=False)
    else:
        logfile = context.get('Simulation', 'log')
        with open(logfile, 'w') as log:
            system.launch_script(script, stdout=log, stderr=log)
        output.update(f"Simulation log saved in {logfile}", 2)
    output.success('Done')


def reference(args, context):
    """Run reference
    Args:
        args (argparse.NameSpace): namespace from command line parsing
        context (vertools.Context): context
    """
    script = context.get('Reference', 'script')
    output.status("Launching reference script")
    if context.get('Reference', 'disable_log') is True:
        system.launch_script(script, stdout=False, stderr=False)
    else:
        logfile = context.get('Reference')
        with open(logfile, 'w') as log:
            system.launch_script(script, stdout=log, stderr=log)
        output.update(f"Reference log saved in {logfile}", 2)
    output.success('Done')


def compare_results(args, context):
    """Compare simulation & reference results
    Args:
        args (argparse.NameSpace): namespace from command line parsing
        context (vertools.Context): context
    """
    simresults_name = context.get('Simulation', 'results')
    refresults_name = context.get('Reference', 'results')
    simresults = None
    refresults = None
    try:
        simresults = open(simresults_name, 'r')
    except OSError:
        output.error(f"Could not open file {simresults_name}")
        exit(1)
    try:
        refresults = open(refresults_name, 'r')
    except OSError:
        output.error(f"Could not open file {refresults_name}")
        exit(1)
    # Check file lengths
    sim_length = sum(1 for line in simresults)
    ref_length = sum(1 for line in refresults)
    if sim_length != ref_length:
        output.error(f"File length mismatch: {simresults_name} has {sim_length} lines; "
                     f"{refresults_name} has {ref_length} lines.", 2)
    # Compare files line by line
    threshold = context.get('Validation', 'threshold')
    simresults.seek(0)
    refresults.seek(0)
    for line, (sim, ref) in enumerate(zip(simresults, refresults)):
        if abs(sim - ref) > threshold:
            output.error(f"Results mismatch on line {line}: reference={ref}, simulation={sim}", 2)


def validate(args, context):
    """Run simulation and reference and then compare results
    Args:
        args (argparse.NameSpace): namespace from command line parsing
        context (vertools.Context): context
    """
    pass