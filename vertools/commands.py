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
        """Initialize files, context, variables, ...
        Returns:
            bool: True if command needs to continue, False to abort
        """
        return True

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
            return output_func(*args, **kwargs)

    def __call__(self):
        setup_status = self.setup()
        if setup_status is False:
            return
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
        fname = self.context.get('Input', 'file')
        folder = os.path.abspath(fname)[:-len(fname)]
        if not system.exists(folder):
            self.output(output.error, f"Input file cannot be created: path `{folder}` does not exist")
            exit(3)
        if fname in os.listdir(folder):
            confirm = self.output(output.confirm, f"File {fname} already exists. Do you want to replace it?", True)
            if confirm is True:
                self.output(output.update, "Removing old file...", 2)
                system.remove_files(fname)
            else:
                return False
        return True

    def run(self):
        self.context.set('CommandLine', 'waveform', self.args.waveform)
        signal = waveforms.generate(self.context)
        fname = self.context.get('Input', 'file')
        np.savetxt(fname, signal, fmt='%d')
        self.output(output.success, f"Saved {len(signal)} samples on file `{fname}`")


class SimulateCommand(CommandAPI):
    def setclock(self):
        clock = self.context.get('Simulation', 'clock')
        clockgen = self.context.get('Simulation', 'clock_gen')
        if not system.exists(clockgen):
            self.output(output.error, f"Clock generator {clockgen} does not exist")
            exit(7)
        # Clockgen is a small file, store it in memory
        with open(clockgen, 'r') as f:
            lines = f.readlines()
        # Overwrite
        with open(clockgen, 'w') as f:
            for line in lines:
                # Find constant declaration line
                if 'constant Ts' not in line:
                    f.write(line)
                else:
                    pos = line.find(':=')
                    f.write(line[:pos + len(':=')] + f" {clock};\n")

    def setup(self):
        # Remove work folder
        self.output(output.status, "Setting up simulation")
        self.output(output.update, "Setting clock", 2)
        self.setclock()
        self.output(output.update, "Removing work/ folder", 2)
        system.run_bash('rm -rf work/')
        self.output(output.update, "Removing old simulation results", 2)
        system.remove_files(self.context.get('Simulation', 'results'))
        self.output(output.success, 'Done')

    def run(self):
        self.output(output.status, "Running simulation")
        setup_command = self.context.get('Simulation', 'setup', '')
        simul_command = self.context.get('Simulation', 'command')
        command = [command for command in (setup_command, simul_command) if command != '']
        self.output(output.update, "Launching simulation command", 2)
        if self.context.get('Simulation', 'disable_log') is True:
            system.run_bash(command, stdout=False, stderror=False)
        else:
            logfile = self.context.get('Simulation', 'log')
            with open(logfile, 'w') as log:
                system.run_bash(command, stdout=log, stderr=log)
            self.output(output.update, f"Simulation log saved in {logfile}", 2)
        self.output(output.success, 'Done')

    def exit(self):
        # Check if results were created
        self.output(output.status, "Checking folder")
        if not system.exists(self.context.get('Simulation', 'results')):
            self.output(output.error, f"Results file was not generated")
            exit(5)
        self.output(output.success, "Done")


class CompareCommand(CommandAPI):
    def setup(self):
        self.output(output.status, "Checking results folder")
        simresults_name = self.context.get('Simulation', 'results')
        refresults_name = self.context.get('Reference', 'results')
        for file in simresults_name, refresults_name:
            if not system.exists(file):
                self.output(output.error, f"File {file} does not exist. Cannot compare results")
                exit(4)
        self.output(output.success, "All files are present", 2)
        return True

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
            self.output(output.error, f"Could not open file {simresults_name}", 2)
            exit(1)
        try:
            refresults = open(refresults_name, 'r')
        except OSError:
            self.output(output.error, f"Could not open file {refresults_name}", 2)
            exit(1)
        self.output(output.update, f"Comparing `{simresults_name}` and `{refresults_name}`", 2)
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
    def setup(self):
        self.output(output.status, "Setting up reference")
        self.output(output.update, "Removing old reference results", 2)
        system.remove_files(self.context.get('Reference', 'results'))
        return True

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

    def exit(self):
        # Check if results were created
        self.output(output.status, "Checking reference folder")
        if not system.exists(self.context.get('Reference', 'results')):
            self.output(output.error, f"Results file was not generated", 2)
            exit(5)
        self.output(output.success, "Done")


class VerifyCommand(CommandAPI):
    def run(self):
        sim = SimulateCommand(self.args, self.context, self.verbose)
        ref = ReferenceCommand(self.args, self.context, self.verbose)
        com = CompareCommand(self.args, self.context, self.verbose)
        sim()
        ref()
        com()
