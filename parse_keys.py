#!/usr/bin/env python3

from lib.diagnosis_keys import *
from lib.scanned_rpis import *
from lib.ramble_rpis import *
from lib.rpis_in_db import *
from lib.conversions import *
from lib.crypto import *
import argparse
import plyvel
import struct
import lib.contact_records_pb2
from lib.diagnosis_key import DiagnosisKey
from lib.count_users import count_users

parser = argparse.ArgumentParser(description="Exposure Notification Diagnosis Key Parser.",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-d", "--diagnosiskeys", type=str, default="testExport-2-records-1-of-1.zip",
                    help="file name of the Diagnosis Keys .zip file")
parser.add_argument("-c", "--contactrecords", type=str, default="",
                    help="directory name of a contact record LevelDB (e.g. app_contact-tracing-contact-record-db/)")
parser.add_argument("-r", "--rpis", type=str, default="",
                    help="file name of a Scanned RPIs .csv file")
parser.add_argument("--ramble_rpis", type=str, default="",
                    help="file name of a RamBLE sqlite file")
parser.add_argument("-s", "--short", action="store_true",
                    help="show only one scan per match")
parser.add_argument("-l", "--localtime", action="store_true",
                    help="display timestamps in local time (otherwise the default is UTC)")
parser.add_argument("-u", "--usercount", action="store_true",
                    help="count the number of users who submitted Diagnosis Keys")
parser.add_argument("-m", "--multiplier", type=int, default=10,
                    help="padding multiplier (RANDOM_KEY_PADDING_MULTIPLIER as set on cwa-server)")
parser.add_argument("-a", "--auto-multiplier", action="store_true",
                    help="automatically detect the multiplier (range 1..10)")
parser.add_argument("-n", "--new-android-apps-only", action="store_true",
                    help="assume that no 'old' Android apps uploaded keys")
args = parser.parse_args()

dk_file_name = args.diagnosiskeys
rpi_file_name = args.rpis
ramble_file_name = args.ramble_rpis
read_rpi_file = (rpi_file_name != "")
read_ramble_file = (ramble_file_name != "")
contactrecord_dir_name = args.contactrecords
read_contact_record_db = (contactrecord_dir_name != "")

print("Exposure Notification Diagnosis Key Parser")
print("This script parses published Diagnosis Keys.\n")
# see https://github.com/google/exposure-notifications-server/tree/master/examples/export

dk = DiagnosisKeys(dk_file_name)
print("File '%s' read." % dk_file_name)

contactrecord_db = None
if read_contact_record_db:
    contactrecord_db = plyvel.DB(contactrecord_dir_name)
    rpis_in_db = RPIinLevelDB(contactrecord_db)

scanned_rpis = None
if read_rpi_file:
    scanned_rpis = ScannedRPIs(rpi_file_name)
    print("File '%s' read." % rpi_file_name)

ramble_rpis = None
if read_ramble_file:
    ramble_rpis = RambleRPIs(ramble_file_name)
    print("File '%s' read." % ramble_file_name)

start_timestamp = dk.get_upload_start_timestamp()
end_timestamp = dk.get_upload_end_timestamp()
if args.localtime:
    start_timestamp = get_local_datetime(start_timestamp)
    end_timestamp = get_local_datetime(end_timestamp)
print("- Time window: %s - %s" % (get_string_from_datetime(start_timestamp),
                                  get_string_from_datetime(end_timestamp)))
print("- Region: %s" % dk.get_region())
print("- Batch: %d of %d" % (dk.get_batch_num(), dk.get_batch_size()))

for signature_info in dk.get_signature_infos():
    print("- Signature Info:")
    print(signature_info)

dk_list = []

keys = None
for i in [0, 1]:
    if i == 0:
        keys = dk.get_keys()
        print("Diagnosis Keys:")
    elif i == 1:
        keys = dk.get_revised_keys()
        print("\nRevised Diagnosis Keys:")
    if len(keys) == 0:
        print("(none)")
    i = 0
    for tek in keys:
        i += 1
        start_timestamp = get_datetime_from_utc_timestamp(get_timestamp_from_interval(tek.rolling_start_interval_number))
        end_timestamp = get_datetime_from_utc_timestamp(get_timestamp_from_interval(tek.rolling_start_interval_number+tek.rolling_period))
        if args.localtime:
            start_timestamp = get_local_datetime(start_timestamp)
            end_timestamp = get_local_datetime(end_timestamp)
        print("%3d: TEK: %s, Transmission Risk Level: %s, Validity: %s - %s (%d, %d)" %
              (i, tek.key_data.hex(), tek.transmission_risk_level,
               get_string_from_datetime(start_timestamp),
               get_string_from_datetime(end_timestamp),
               tek.rolling_start_interval_number, tek.rolling_period),
              end='')
        if tek.HasField("report_type"):
            field_types = ["UNKNOWN", "CONFIRMED_TEST", "CONFIRMED_CLINICAL_DIAGNOSIS",
                           "SELF_REPORT", "RECURSIVE", "REVOKED"]
            print (", Report Type: %s" % field_types[tek.report_type], end='')
        if tek.HasField("days_since_onset_of_symptoms"):
            print (", Days since onset of symptoms: %d" % tek.days_since_onset_of_symptoms, end='')
        print()

        if read_contact_record_db:
            rpi_key = derive_rpi_key(tek.key_data)
            for diagnosis_rpi in create_list_of_rpis_for_interval_range(rpi_key, tek.rolling_start_interval_number,
                                                                        tek.rolling_period):
                if diagnosis_rpi in rpis_in_db.rpis_dict:
                    print("FOUND MATCH!")
                    aem_key = derive_aem_key(tek.key_data)
                    interval = get_interval_number_from_rpi(diagnosis_rpi, rpi_key)
                    interval_timestamp1 = get_datetime_from_utc_timestamp(get_timestamp_from_interval(interval))
                    interval_timestamp2 = get_datetime_from_utc_timestamp(get_timestamp_from_interval(interval+1))
                    if args.localtime:
                        interval_timestamp1 = get_local_datetime(interval_timestamp1)
                        interval_timestamp2 = get_local_datetime(interval_timestamp2)
                    print("RPI Validity:", get_string_from_datetime(interval_timestamp1),
                          "-", get_string_from_datetime(interval_timestamp2),
                          "(Interval number: %d," % interval,
                          "RPI: %s)" % diagnosis_rpi.hex())

                    aem_key = derive_aem_key(tek.key_data)
                    day = rpis_in_db.rpis_dict[diagnosis_rpi]
                    # each "key" entry in the LevelDB has 18 bytes: 2 bytes "day" and 16 bytes "rpi"
                    dbkey = struct.pack(">H16s", day, diagnosis_rpi)
                    dbvalue = contactrecord_db.get(dbkey)
                    # each "value" entry is a ProtocolBuffer-encoded message, length at least 1
                    contact_records = lib.contact_records_pb2.ContactRecords()
                    contact_records.ParseFromString(dbvalue)
                    for scanrecord in contact_records.scanrecord:
                        metadata = decrypt_aem(aem_key, scanrecord.aem, diagnosis_rpi)
                        if metadata[0] >= 0x40:
                            tx_power = struct.unpack_from("b", metadata, 1)[0]  # signed char
                        else:
                            tx_power = 0
                            print("--> WARNING: Expected metadata to start with at least 0x40, so this could be a false positive!")

                        sr_timestamp = get_datetime_from_utc_timestamp(scanrecord.timestamp)
                        if args.localtime:
                            sr_timestamp = get_local_datetime(sr_timestamp)
                        attenuation = tx_power-scanrecord.rssi
                        print(get_string_from_datetime(sr_timestamp),
                              "Attenuation: %ddB" % attenuation,
                              "(RSSI: %ddBm, AEM: %s, Metadata: % s)" % (scanrecord.rssi, scanrecord.aem.hex(), metadata.hex()))
                        if args.short:
                            print("(...)")
                            break

        if read_rpi_file:
            for diagnosis_rpi in create_list_of_rpis_for_interval_range(derive_rpi_key(tek.key_data),
                                                                        tek.rolling_start_interval_number, tek.rolling_period):
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
                        if args.short:
                            print("(...)")
                            break

        if read_ramble_file:
            for diagnosis_rpi in create_list_of_rpis_for_interval_range(derive_rpi_key(tek.key_data),
                                                                        tek.rolling_start_interval_number, tek.rolling_period):
                if diagnosis_rpi in ramble_rpis.rpis_dict:
                    print("FOUND MATCH!")
                    aem_key = derive_aem_key(tek.key_data)
                    ramble_rpi_entries = ramble_rpis.rpis_dict[diagnosis_rpi]
                    for ramble_rpi_entry in ramble_rpi_entries:
                        metadata = decrypt_aem(aem_key, ramble_rpi_entry.aem, diagnosis_rpi)
                        print("Timeframe: %s - %s (%d seconds), RSSI: %d dBm, LAT, LON, altitude, speed: %s, %s, %s, %s" %
                              (get_string_from_datetime(get_local_datetime(ramble_rpi_entry.start_time)),
                               get_string_from_datetime(get_local_datetime(ramble_rpi_entry.end_time)),
                               (ramble_rpi_entry.end_time-ramble_rpi_entry.start_time).total_seconds(),
                               ramble_rpi_entry.rssi,
                               ramble_rpi_entry.lat, ramble_rpi_entry.lon,
                               ramble_rpi_entry.altitude, ramble_rpi_entry.speed))
                        print("Decrypted metadata: %s " % metadata.hex(), end='')
                        if metadata[0] == 0x40:
                            tx_power = struct.unpack_from("b", metadata, 1)[0]  # signed char
                            print("--> TX Power: %d dBm --> RF attenuation: %d dB" %
                                  (tx_power, tx_power-ramble_rpi_entry.rssi), end='')
                        else:
                            print("--> WARNING: Expected metadata to start with 40, so this could be a false positive!")
                        print()
                        if args.short:
                            print("(...)")
                            break

        if args.usercount:
            dk_list.append(DiagnosisKey(tek.key_data, tek.rolling_start_interval_number, tek.rolling_period, tek.transmission_risk_level))

if read_contact_record_db:
    contactrecord_db.close()

if args.usercount:
    count_users(dk_list, multiplier = args.multiplier, auto_multiplier_detect = args.auto_multiplier,
                new_android_apps_only = args.new_android_apps_only)
