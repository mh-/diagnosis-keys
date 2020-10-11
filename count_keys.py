#!/usr/bin/env python3

from lib.diagnosis_keys import *
from lib.conversions import *
import argparse
from lib.diagnosis_key import DiagnosisKey
from lib.count_users_v1_5 import count_users

parser = argparse.ArgumentParser(description="Exposure Notification Diagnosis Key Parser / Counter.",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-d", "--diagnosiskeys", type=str,
                    help="file name of the Diagnosis Keys .zip file")
parser.add_argument("-t", "--print-metadata", action="store_true",
                    help="print metadata from the Diagnosis Keys .zip file")
parser.add_argument("-k", "--print-keys", action="store_true",
                    help="print all keys from the Diagnosis Keys .zip file")
parser.add_argument("-m", "--multiplier", type=int, default=5,
                    help="padding multiplier (RANDOM_KEY_PADDING_MULTIPLIER as set on cwa-server)")
parser.add_argument("-a", "--auto-multiplier", action="store_true",
                    help="automatically detect the multiplier (range 1..10)")
args = parser.parse_args()

dk_file_name = args.diagnosiskeys

print("Exposure Notification Diagnosis Key Parser / Counter")
print("This script counts published Diagnosis Keys.\n")
# see https://github.com/google/exposure-notifications-server/tree/master/examples/export

dk = DiagnosisKeys(dk_file_name)
print("File '%s' read." % dk_file_name)

start_timestamp = dk.get_upload_start_timestamp()
end_timestamp = dk.get_upload_end_timestamp()
if args.print_metadata:
    print("- Time window: %s - %s" % (get_string_from_datetime(start_timestamp),
                                      get_string_from_datetime(end_timestamp)))
    print("- Region: %s" % dk.get_region())
    print("- Batch: %d of %d" % (dk.get_batch_num(), dk.get_batch_size()))
    print("- # of keys in batch: %d" % len(dk.get_keys()))

    for signature_info in dk.get_signature_infos():
        print("- Signature Info:")
        print(signature_info)

dk_list = []

keys = None
for _ in [0, 1]:
    if _ == 0:
        keys = dk.get_keys()
        if args.print_keys:
            print("Diagnosis Keys:")
    elif _ == 1:
        keys = dk.get_revised_keys()
        if args.print_keys:
            print("\nRevised Diagnosis Keys:")
    if args.print_keys:
        if len(keys) == 0:
            print("(none)\n")

    count = 0
    for tek in keys:
        count += 1
        start_timestamp = \
            get_datetime_from_utc_timestamp(get_timestamp_from_interval(tek.rolling_start_interval_number))
        end_timestamp = \
            get_datetime_from_utc_timestamp(get_timestamp_from_interval(tek.rolling_start_interval_number +
                                                                        tek.rolling_period))

        if args.print_keys:
            print("%5d: TEK: %s, Transmission Risk Level: %s, Validity: %s - %s (%d, %d)" %
                  (count, tek.key_data.hex(), tek.transmission_risk_level,
                   get_string_from_datetime(start_timestamp),
                   get_string_from_datetime(end_timestamp),
                   tek.rolling_start_interval_number, tek.rolling_period),
                  end='')
            if tek.HasField("report_type"):
                field_types = ["UNKNOWN", "CONFIRMED_TEST", "CONFIRMED_CLINICAL_DIAGNOSIS",
                               "SELF_REPORT", "RECURSIVE", "REVOKED"]
                print(", Report Type: %s" % field_types[tek.report_type], end='')
            if tek.HasField("days_since_onset_of_symptoms"):
                print(", Days since onset of symptoms: %d" % tek.days_since_onset_of_symptoms, end='')
            print()

        dk_list.append(DiagnosisKey(tek.key_data, tek.rolling_start_interval_number, tek.rolling_period,
                                    tek.transmission_risk_level))

count_users(dk_list, padding_multiplier=args.multiplier, auto_multiplier_detect=args.auto_multiplier)
