import os
import string
import numpy as np
import engfmt

import vertools.output as output
import vertools.system as system
import vertools.waveforms as waveforms


class CommandAPI:
    def __init__(self, args, context, verbose=True):
        self.args = args
        self.context = context
        self.verbose = verbose
        self.data = {}

    def setup(self):
        """Initialize context, environment and variables"""
        pass

    def run(self):
        """Run core actions"""
        pass

    def exit(self):
        """Post execution actions"""
        pass

    def output(self, output_func=output.update, *args, **kwargs):
        """Generate an output through a generic function only if command is set to verbose
        Args:
            output_func (function): output function (usually print or output.update)
            *args: output_func arguments
            **kwargs: output_func keyword arguments
        """
        if self.verbose is True:
            output_func(*args, **kwargs)

    def __call__(self):
        self.setup()
        self.run()
        self.exit()


class CleanCommand(CommandAPI):
    def setup(self):
        self.data['targets'] = {
            'Simulation': ['results', 'log'],
            'Reference': ['results', 'log']
        }

    def run(self):
        self.output(output.status, 'Cleaning files')
        for section, parameters in self.data['targets'].items():
            for parameter in self.data['targets'][section]:
                fname = self.context.get(section, parameter)
                try:
                    os.remove(fname)
                except OSError:
                    pass
                self.output(output.update, f"Removed {fname}", 2)
            self.output(output.success('Done'))


class GenerateInputsCommand(CommandAPI):
    def setup(self):
        self.context.set('CommandLine', 'waveform', self.args.waveform)

    def run(self):
        signal = waveforms.generate(self.context)
        fname = self.context.get('Input', 'file')
        np.savetxt(fname, signal, fmt='%d')
        self.output(output.success, f"Saved {len(signal)} samples on file {fname}")


class SimulateCommand(CommandAPI):
    def setup(self):
        setup_command = self.context.get('Simulation', 'setup')
        if setup_command != '':
            self.data['command'] = f"{setup_command} && "
        # Remove work folder
        system.run_bash('rm -rf work/')

    def run(self):
        self.output(output.status, "Running simulation")
        duration = self.context.get('Simulation', 'tend') - self.context.get('Simulation', 'tstart')
        duration = engfmt.Quantity(duration, 's')
        command = string.Template(self.context.get('Simulation', 'command'))
        command = command.substitute(duration=duration.to_eng())
        command = self.data.get('command', '') + command
        if self.context.get('Simulation', 'disable_log') is True:
            system.run_bash(command, stdout=False, stderror=False)
        else:
            logfile = self.context.get('Simulation', 'log')
            with open(logfile, 'w') as log:
                system.run_bash(command, stdout=log, stderr=log)
            self.output(output.update, f"Simulation log saved in {logfile}", 2)
        self.output(output.success, 'Done')


class CompareCommand(CommandAPI):
    def run(self):
        """Compare simulation and reference results"""
        self.output(output.status, "Comparing results")
        simresults_name = self.context.get('Simulation', 'results')
        refresults_name = self.context.get('Reference', 'results')
        simresults = None
        refresults = None
        try:
            simresults = open(simresults_name, 'r')
        except OSError:
            self.output(output.error, f"Could not open file {simresults_name}")
            exit(1)
        try:
            refresults = open(refresults_name, 'r')
        except OSError:
            self.output(output.error, f"Could not open file {refresults_name}")
            exit(1)
        self.output(output.update, f"Comparing files `{simresults_name}` and `{refresults_name}`...")
        # Check file lengths
        sim_length = sum(1 for line in simresults)
        ref_length = sum(1 for line in refresults)
        if sim_length != ref_length:
            output.error(f"File length mismatch: {simresults_name} has {sim_length} lines; "
                         f"{refresults_name} has {ref_length} lines.", 2)
            exit(2)
        # Compare files line by line
        threshold = self.context.get('Verification', 'threshold')
        simresults.seek(0)
        refresults.seek(0)
        for line, (sim, ref) in enumerate(zip(simresults, refresults)):
            sim = int(sim)
            ref = int(ref)
            if abs(sim - ref) > threshold:
                self.output(output.error, f"Results mismatch on line {line+1}: reference={ref}, simulation={sim}", 2)
                exit(3)
        self.output(output.success, "All results are matching")


class ReferenceCommand(CommandAPI):
    def run(self):
        command = self.context.get('Reference', 'command')
        self.output(output.status, "Launching reference command")
        if self.context.get('Reference', 'disable_log') is True:
            system.run_bash(command, stdout=False, stderr=False)
        else:
            logfile = self.context.get('Reference', 'log')
            with open(logfile, 'w') as log:
                system.run_bash(command, stdout=log, stderr=log)
            self.output(output.update, f"Reference log saved in {logfile}", 2)
        self.output(output.success, 'Done')


class ValidateCommand(CommandAPI):
    def run(self):
        sim = SimulateCommand(self.args, self.context, self.verbose)
        ref = SimulateCommand(self.args, self.context, self.verbose)
        sim()
        ref()
