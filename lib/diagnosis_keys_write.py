import random

import TemporaryExposureKeyExportV1_5_pb2
import zipfile
import secrets
from lib.conversions import *

TRL_PROFILE = [5, 6, 8, 8, 8, 5, 3, 1, 1, 1, 1, 1, 1, 1]  # 0: today, 1: yesterday, ...

NUMBER_OF_UPLOAD_DAYS = 14
NUMBER_OF_UPLOADS_PER_DAY_MIN = 5
NUMBER_OF_UPLOADS_PER_DAY_MAX = 20
ENIN_ONE_DAY = 144
LAST_DAY = "2020-05-23-+0000"


class DiagnosisKeysWriter:
    def __init__(self, file_name):

        self.diagnosis_keys_export_data = TemporaryExposureKeyExportV1_5_pb2.TemporaryExposureKeyExport()

        last_day = datetime.datetime.strptime(LAST_DAY, "%Y-%m-%d-%z")
        last_enin = get_interval_from_utc_timestamp(get_timestamp_from_utc_datetime(last_day))
        for upload_enin in range(last_enin, last_enin-int(NUMBER_OF_UPLOAD_DAYS*ENIN_ONE_DAY), -ENIN_ONE_DAY):
            number_of_uploads_per_day = random.randint(NUMBER_OF_UPLOADS_PER_DAY_MIN, NUMBER_OF_UPLOADS_PER_DAY_MAX)
            for _ in range(number_of_uploads_per_day):
                for pos in range(13):
                    key_data = secrets.token_bytes(16)
                    # key_data = bytes.fromhex("a45f81ba2b2c533edbe87a3db47733c4")
                    trl = TRL_PROFILE[pos+1]
                    start_enin = upload_enin - (pos+1)*ENIN_ONE_DAY
                    duration = ENIN_ONE_DAY
                    report_type = TemporaryExposureKeyExportV1_5_pb2.TemporaryExposureKey.ReportType.CONFIRMED_TEST
                    self.add_key(key_data, trl, start_enin, duration, report_type)

        export_bin = self.diagnosis_keys_export_data.SerializeToString()

        # The binary format file consists of a 16 byte header,
        # containing "EK Export v1​" right padded with whitespaces in UTF-8
        label = "EK Export v1"
        header_str = label + ' ' * (16-len(label))
        header = header_str.encode("UTF-8")

        export_bin = header + export_bin
        # print(export_bin)

        zip_file = zipfile.ZipFile(file_name, mode='w', compression=zipfile.ZIP_DEFLATED)
        zip_file.writestr("export.bin", export_bin)

    def add_key(self, key_data, trl, start, duration, report_type):
        key = self.diagnosis_keys_export_data.keys.add()
        assert len(key_data) == 16
        key.key_data = key_data
        assert trl >= 1, trl <= 8
        key.transmission_risk_level = trl
        assert start > 0
        key.rolling_start_interval_number = start
        assert duration <= 144
        key.rolling_period = duration
        assert report_type >= 0, report_type <= 5
        key.report_type = report_type
