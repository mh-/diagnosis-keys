#!/usr/bin/env python3

from lib.diagnosis_keys import *
from lib.scanned_rpis import *
from lib.conversions import *
from lib.crypto import *
import argparse

parser = argparse.ArgumentParser(description="Exposure Notification Diagnosis Key Parser.")
parser.add_argument("-d", "--diagnosiskeys", type=str, default="testExport-2-records-1-of-1.zip",
                    help="file name of the Diagnosis Keys .zip file")
parser.add_argument("-r", "--rpis", type=str, default="",
                    help="file name of the Scanned RPIs .csv file")
args = parser.parse_args()

dk_file_name = args.diagnosiskeys
rpi_file_name = args.rpis
read_rpi_file = (rpi_file_name != "")

print("Exposure Notification Diagnosis Key Parser")
print("This script parses published Diagnosis Keys.\n")
# see https://github.com/google/exposure-notifications-server/tree/master/examples/export

dk = DiagnosisKeys(dk_file_name)
print("File '%s' read." % dk_file_name)

scanned_rpis = None
if read_rpi_file:
    scanned_rpis = ScannedRPIs(rpi_file_name)
    print("File '%s' read." % rpi_file_name)

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

    if read_rpi_file:
        for diagnosis_rpi in get_rpis(derive_rpi_key(tek.key_data), tek.rolling_start_interval_number, tek.rolling_period):
            # print(diagnosis_rpi, end='')
            if diagnosis_rpi in scanned_rpis.rpis_dict:
                print("FOUND MATCH!")
                aem_key = derive_aem_key(tek.key_data)
                scanned_rpi_entries = scanned_rpis.rpis_dict[diagnosis_rpi]
                for scanned_rpi_entry in scanned_rpi_entries:
                    metadata = decrypt_aem(aem_key, scanned_rpi_entry.aem, diagnosis_rpi)
                    print("Timeframe: %s - %s (%d seconds), RSSI: %d dBm, LAT, LON, altitude, speed: %s, %s, %s, %s" %
                          (get_string_from_datetime(get_local_datetime(scanned_rpi_entry.start_time)),
                           get_string_from_datetime(get_local_datetime(scanned_rpi_entry.end_time)),
                           (scanned_rpi_entry.end_time-scanned_rpi_entry.start_time).total_seconds(),
                           scanned_rpi_entry.rssi,
                           scanned_rpi_entry.lat, scanned_rpi_entry.lon,
                           scanned_rpi_entry.altitude, scanned_rpi_entry.speed))
                    print("Decrypted metadata: %s " % metadata.hex(), end='')
                    if metadata[0] == 0x40:
                        tx_power = struct.unpack_from("b", metadata, 1)[0]  # signed char
                        print("--> TX Power: %d dBm --> RF attenuation: %d dB" %
                              (tx_power, tx_power-scanned_rpi_entry.rssi), end='')
                    else:
                        print("--> WARNING: Expected metadata to start with 40, so this could be a false positive!")
                    print()
        # print()
