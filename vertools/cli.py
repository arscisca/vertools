import argparse

import vertools.commands as commands
import engfmt


class Contextualize(argparse.Action):
    SECTIONS = {}

    def __init__(self,
                 option_strings,
                 dest,
                 section='CommandLine',
                 parameters=None,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar=None):
        super(Contextualize, self).__init__(option_strings, dest, nargs, const, default, type, choices, required, help,
                                            metavar)
        self.section = section
        if parameters is not None:
            self.parameters = parameters
        else:
            self.parameters = self.dest
        if self.section not in self.SECTIONS:
            self.SECTIONS[section] = {}

    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(values, list):
            if len(values) == 0:
                values = True
        # Normally set the attribute
        setattr(namespace, self.dest, values)
        # Update dictionary
        if isinstance(self.parameters, list):
            for parameter, value in zip(self.parameters, values):
                self.SECTIONS[self.section][parameter] = value
        else:
            self.SECTIONS[self.section][self.parameters] = values


# Main parser
vertools = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description='High level simulation tool for digital circuit verification'
)
vertools.add_argument(
    '--config',
    help='configuration file',
    metavar='FILE',
    dest='local_config',
    default=None
)
subparsers = vertools.add_subparsers(
    title='command',
    description='vertools command'
)

# Command parsers
# Simulate
simulate = subparsers.add_parser(
    'simulate',
    help='run simulation',
)
simulate.add_argument(
    '-c', '--command',
    help='simulation script',
    action=Contextualize,
    section='Simulation',
    parameters='command'
)
me = simulate.add_mutually_exclusive_group()
me.add_argument(
    '--no-log',
    help='disable logging',
    dest='log',
    nargs=0,
    action=Contextualize,
    section='Simulation',
    parameters='disable_log'
)
me.add_argument(
    '--log',
    help='specify logging file name',
    action=Contextualize,
    section='Simulation',
    parameters='log'
)
simulate.set_defaults(func=commands.SimulateCommand)

# Reference
reference = subparsers.add_parser(
    'reference',
    help='run reference executable'
)
reference.add_argument(
    '-c', '--command',
    help='reference command',
    action=Contextualize,
    section='Reference',
    parameters='command'
)
me = reference.add_mutually_exclusive_group()
me.add_argument(
    '--no-log',
    help='disable logging',
    dest='log',
    nargs=0,
    action=Contextualize,
    section='Reference',
    parameters='disable_log'
)
me.add_argument(
    '--log',
    help='specify logging file name',
    action=Contextualize,
    section='Reference',
    parameters='log'
)
reference.set_defaults(
    func=commands.ReferenceCommand
)

# Compare
compare = subparsers.add_parser(
    'compare',
    help='compare simulation and reference results'
)
compare.add_argument(
    '-s', '--simulation',
    help='simulation results file',
    action=Contextualize,
    section='Simulation',
    parameters='results'
)
compare.add_argument(
    '-r', '--reference',
    help='reference results file',
    action=Contextualize,
    section='Reference',
    parameters='results'
)
compare.add_argument(
    '-t', '--threshold',
    help='comparison threshold',
    type=int,
    action=Contextualize,
    section='Verification'
)
compare.set_defaults(
    func=commands.CompareCommand
)

# Validate
validate = subparsers.add_parser(
    'validate',
    help='run the full validation suite: simulation, reference and comparison'
)

# Input generation
generate_inputs = subparsers.add_parser(
    'generate-inputs',
    help='generate inputs'
)
generate_inputs.add_argument(
    '-f', '--filename',
    help='file name to store inputs',
    metavar='FILENAME',
    dest='file',
    action=Contextualize,
    section='Input'
)
generate_inputs.add_argument(
    '-t', '--time',
    nargs=3,
    type=engfmt.Quantity,
    help='time information. In order, tstart, tend and tstep',
    section='Input',
    parameters=['tstart', 'tend', 'tstep'],
    action=Contextualize
)
subparsers = generate_inputs.add_subparsers(
    title='waveform',
    description='input waveform',
    dest='waveform'
)
# Constant
parser = subparsers.add_parser(
    'constant',
    help='constant signal'
)
parser.add_argument(
    'value',
    help='constant value',
    section='CommandLine',
    type=int,
    action=Contextualize,
)
# Sine
parser = subparsers.add_parser(
    'sine',
    help='sine wave'
)
parser.add_argument(
    'amplitude',
    help='sine wave amplitude',
    type=int,
    action=Contextualize,
)
parser.add_argument(
    'frequency',
    help='sine wave frequency',
    type=engfmt.Quantity,
    action=Contextualize,
)
parser.add_argument(
    'phase',
    help='sine wave phase (in radians)',
    type=float,
    action=Contextualize,
)
generate_inputs.set_defaults(
    func=commands.GenerateInputsCommand
)
# Chirp
parser = subparsers.add_parser(
    'chirp',
    help='chirp signal'
)
parser.add_argument(
    'amplitude',
    help='chirp signal amplitude',
    type=int,
    action=Contextualize
)
parser.add_argument(
    'duration',
    help='chirp signal duration',
    type=engfmt.Quantity,
    action=Contextualize
)
parser.add_argument(
    'f0',
    help='initial frequency',
    type=engfmt.Quantity,
    action=Contextualize
)
parser.add_argument(
    'f1',
    help='final frequency',
    type=engfmt.Quantity,
    action=Contextualize
),
parser.add_argument(
    '--method',
    help='chirp generation option',
    choices=['linear', 'quadratic', 'logarithmic', 'hyperbolic'],
    default='linear',
    action=Contextualize,
    section='CommandLine',
    parameters='method'
)


def parse(args=None):
    return vertools.parse_args(args)
