from argparse import ArgumentParser
from .files import get_input_output_paths
from .transformers import transform
from . import const


def main():
    parser = ArgumentParser('py-backwars')
    parser.add_argument('-i', '--input', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)
    parser.add_argument('-t', '--target', type=str,
                        required=True, choices=const.TARGETS.keys())
    args = parser.parse_args()

    for paths in get_input_output_paths(args.input, args.output):
        with paths.input.open() as f:
            code = f.read()

        transformed = transform(code, const.TARGETS[args.target])

        try:
            paths.output.parent.mkdir(parents=True)
        except FileExistsError:
            pass

        with paths.output.open('w') as f:
            f.write(transformed)