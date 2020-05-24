from lib.conversions import *
from lib.crypto import *
import TemporaryExposureKeyExport_pb2
from zipfile import ZipFile
import datetime

file_name = "testExport-2-records-1-of-1.zip"
# file_name = "testExport-450-records-1-of-5.zip"

# The binary format file consists of a 16 byte header, containing "EK Export v1​" right padded with whitespaces in UTF-8
label = "EK Export v1"
header_str = label + ' ' * (16-len(label))
header = header_str.encode("UTF-8")

zip_file = ZipFile(file_name)
export_bin = zip_file.read("export.bin")

if not export_bin[:len(header)] == header:
    print("ERROR: export.bin (extracted from %s) does not start with '%s'" % (file_name, header_str))
    exit(1)

tek_keys_export = TemporaryExposureKeyExport_pb2.TemporaryExposureKeyExport()
tek_keys_export.ParseFromString(export_bin[len(header):])

# print(tek_keys_export)

print("File '%s' read." % file_name)

start_timestamp_utc = get_datetime_from_utc_timestamp(tek_keys_export.start_timestamp)
end_timestamp_utc = get_datetime_from_utc_timestamp(tek_keys_export.end_timestamp)
print("- Time window: %s - %s" % (get_string_from_datetime(get_local_datetime(start_timestamp_utc)),
                                  get_string_from_datetime(get_local_datetime(end_timestamp_utc))))
print("- Region: %s" % tek_keys_export.region)
print("- Batch: %d of %d" % (tek_keys_export.batch_num, tek_keys_export.batch_size))

for signature_info in tek_keys_export.signature_infos:
    print("- Signature Info:")
    print(signature_info)

print("TEKs:")
i = 0
for tek in tek_keys_export.keys:
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
