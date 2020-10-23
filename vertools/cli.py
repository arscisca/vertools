import argparse

import commands

# Main parser
vertools = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description='High level simulation tool for digital circuit verification'
)
subparsers = vertools.add_subparsers(
    required=True,
    title='command',
    description='vertools command'
)

# Command parsers
# Simulate
simulate = subparsers.add_parser(
    'simulate',
    help='run simulation'
)
simulate.add_argument(
    'script',
    help='simulation script'
)
simulate.add_argument(
    '--config', '-c',
    help='configuration file',
    default='vertools.config'
)
me = simulate.add_mutually_exclusive_group()
me.add_argument(
    '--no-log',
    help='disable logging',
    dest='log',
    action='store_false'
)
me.add_argument(
    '--simlog',
    help='specify logging file name',
    default='simlog.txt'
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
    dest='input'
)
subparsers = generate_inputs.add_subparsers(
    title='waveform',
    description='input waveform',
    dest='waveform',
    required=True
)
parser = subparsers.add_parser(
    'constant',
    help='constant signal'
)
parser.add_argument(
    'value',
    help='constant value',
    type=int
)
parser = subparsers.add_parser(
    'sine',
    help='sine wave'
)
parser.add_argument(
    'amplitude',
    help='sine wave amplitude',
    type=int,
)
parser.add_argument(
    'frequency',
    help='sine wave frequency',
    type=float
)
parser.add_argument(
    'phase',
    help='sine wave phase (in radians)',
    type=float
)
generate_inputs.set_defaults(
    func=commands.generate_inputs
)


def parse(args=None):
    return vertools.parse_args(args)
