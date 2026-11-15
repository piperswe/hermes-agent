"""Offline promotion renderer. Does not contact Kubernetes or write credentials."""
import argparse
from pathlib import Path
import re

SOURCE_SHA = '3b421578588243f920886e6fe79a6faa87ea026e'
VERSION = 'v0.23.1'
IMAGE = 'ghcr.io/piperswe/hermes-agent'


def pin_image(text: str, digest: str) -> str:
    if not re.fullmatch(r'sha256:[0-9a-f]{64}', digest):
        raise ValueError('An immutable sha256 digest is required')
    result, count = re.subn(
        r'(image: )(?:nousresearch/hermes-agent|ghcr.io/piperswe/hermes-agent)@sha256:[0-9a-f]{64}',
        lambda match: match[1] + IMAGE + '@' + digest,
        text,
    )
    if count != 2:
        raise ValueError(f'Expected gateway and configure-honcho images; found {count}')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('digest')
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.write_text(pin_image(args.manifest.read_text(), args.digest))
