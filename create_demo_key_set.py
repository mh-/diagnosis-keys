#!/usr/bin/env python3

from lib.diagnosis_keys_write import *
import argparse

parser = argparse.ArgumentParser(description="Exposure Notification Demo Diagnosis Key Set Generator.",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-d", "--diagnosiskeys", type=str, default="demo_dks.zip",
                    help="file name of the Diagnosis Keys .zip file that should be generated")
args = parser.parse_args()

dk_file_name = args.diagnosiskeys

print("Exposure Notification Demo Diagnosis Key Set Generator")
print("This script generates a Demo Diagnosis Keys Set for apps that parse these keys.\n")

dk = DiagnosisKeysWriter(dk_file_name)
print("File '%s' written." % dk_file_name)

