#!/usr/bin/env python3

from lib.crypto import *
import argparse

parser = argparse.ArgumentParser(description="Derive RPI-Key from TEK.")
parser.add_argument("TEK", type=str,
                    help="TEK (16 bytes hex)")
args = parser.parse_args()

try:
    tek = bytes.fromhex(args.TEK)
    if len(tek) != 16:
        raise ValueError
except ValueError:
    parser.error("TEK must be 16 bytes hex")

# print("TEK: %s" % tek.hex())
print(derive_rpi_key(tek).hex())
