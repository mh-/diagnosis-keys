#!/usr/bin/env python3

from lib.diagnosis_keys import *
from lib.conversions import *
from lib.crypto import *
import argparse

parser = argparse.ArgumentParser(description="Exposure Notification Diagnosis Key Parser.")
parser.add_argument("-d", "--diagnosiskeys", type=str, default="testExport-2-records-1-of-1.zip",
                    help="file name of the Diagnosis Keys .zip file")
args = parser.parse_args()

file_name = args.diagnosiskeys

print("Exposure Notification Diagnosis Key Parser")
print("This script parses published Diagnosis Keys.\n")
# see https://github.com/google/exposure-notifications-server/tree/master/examples/export

dk = DiagnosisKeys(file_name)
print("File '%s' read." % file_name)

start_timestamp_utc = dk.get_upload_start_timestamp()
end_timestamp_utc = dk.get_upload_end_timestamp()
print("- Time window: %s - %s" % (get_string_from_datetime(get_local_datetime(start_timestamp_utc)),
                                  get_string_from_datetime(get_local_datetime(end_timestamp_utc))))
print("- Region: %s" % dk.get_region())
print("- Batch: %d of %d" % (dk.get_batch_num(), dk.get_batch_size()))

for signature_info in dk.get_signature_infos():
    print("- Signature Info:")
    print(signature_info)

print("TEKs:")
i = 0
for tek in dk.get_keys():
    i += 1
    print("%3d: TEK: %s, Transmission Risk Level: %d, Time: %s - %s (%d, %d)" %
          (i, tek.key_data.hex(), tek.transmission_risk_level,
           get_string_from_datetime(get_local_datetime(get_datetime_from_utc_timestamp(get_timestamp_from_interval(
               tek.rolling_start_interval_number)))),
           get_string_from_datetime(get_local_datetime(get_datetime_from_utc_timestamp(get_timestamp_from_interval(
               tek.rolling_start_interval_number+tek.rolling_period)))),
           tek.rolling_start_interval_number, tek.rolling_period))
    print("     RPIs: ", end="")
    for rpi in get_rpis(derive_rpi_key(tek.key_data), tek.rolling_start_interval_number, tek.rolling_period):
        print("%s " % rpi.hex(), end="")
    print()
