#!/usr/bin/env python3
from lib.diagnosis_keys import *
from lib.conversions import *
import argparse
import struct
from lib.count_users import count_users
import json

parser = argparse.ArgumentParser(description="Exposure Notification Diagnosis Key Parser.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-d", "--diagnosiskeys", type=str, default="testExport-2-records-1-of-1.zip", help="file name of the Diagnosis Keys .zip file")
parser.add_argument("-l", "--localtime", action="store_true", help="display timestamps in local time (otherwise the default is UTC)")
args = parser.parse_args()

dk_file_name = args.diagnosiskeys
dk = DiagnosisKeys(dk_file_name)

json_obj = dict()

start_timestamp = dk.get_upload_start_timestamp()
end_timestamp = dk.get_upload_end_timestamp()
if args.localtime:
    start_timestamp = get_local_datetime(start_timestamp)
    end_timestamp = get_local_datetime(end_timestamp)

json_obj["timeWindowStart"] = get_string_from_datetime(start_timestamp)
json_obj["timeWindowEnd"] = get_string_from_datetime(end_timestamp)
json_obj["region"] = dk.get_region()
json_obj["batchNum"] = dk.get_batch_num()
json_obj["batchCount"] = dk.get_batch_size()

json_obj["signatureInfos"] = dict()
for signature_info in dk.get_signature_infos():
    for line in str(signature_info).split("\n"):
        line = line.strip()
        if line:
            json_obj["signatureInfos"][line.split(":")[0]] = line.split(":")[1].replace('"', "").strip()

json_obj["diagnosisKeys"] = []
i = 0
for tek in dk.get_keys():
    i += 1
    start_timestamp = get_datetime_from_utc_timestamp(get_timestamp_from_interval(tek.rolling_start_interval_number))
    end_timestamp = get_datetime_from_utc_timestamp(get_timestamp_from_interval(tek.rolling_start_interval_number + tek.rolling_period))
    if args.localtime:
        start_timestamp = get_local_datetime(start_timestamp)
        end_timestamp = get_local_datetime(end_timestamp)
    key = dict()
    key["TemporaryExposureKey"] = tek.key_data.hex()
    key["transmissionRiskLevel"] = tek.transmission_risk_level
    key["validity"] = dict()
    key["validity"]["start"] = get_string_from_datetime(start_timestamp)
    key["validity"]["end"] = get_string_from_datetime(end_timestamp)
    key["validity"]["rollingStartIntervalNumber"] = tek.rolling_start_interval_number
    key["validity"]["rollingPeriod"] = tek.rolling_period
    json_obj["diagnosisKeys"].append(key)

print(json.dumps(json_obj, indent=2))
