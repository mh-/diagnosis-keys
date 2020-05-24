import TemporaryExposureKeyExport_pb2
from zipfile import ZipFile
from lib.conversions import *


class DiagnosisKeys:
    def __init__(self, file_name):
        zip_file = ZipFile(file_name)
        export_bin = zip_file.read("export.bin")

        # The binary format file consists of a 16 byte header,
        # containing "EK Export v1​" right padded with whitespaces in UTF-8
        label = "EK Export v1"
        header_str = label + ' ' * (16-len(label))
        header = header_str.encode("UTF-8")

        if not export_bin[:len(header)] == header:
            print("ERROR: export.bin (extracted from %s) does not start with '%s'" % (file_name, header_str))
            exit(1)

        self.diagnosis_keys_export_data = TemporaryExposureKeyExport_pb2.TemporaryExposureKeyExport()
        self.diagnosis_keys_export_data.ParseFromString(export_bin[len(header):])

        # print(tek_keys_export)

    def get_keys(self):
        return self.diagnosis_keys_export_data.keys

    def get_upload_start_timestamp(self):
        return get_datetime_from_utc_timestamp(self.diagnosis_keys_export_data.start_timestamp)

    def get_upload_end_timestamp(self):
        return get_datetime_from_utc_timestamp(self.diagnosis_keys_export_data.end_timestamp)

    def get_signature_infos(self):
        return self.diagnosis_keys_export_data.signature_infos

    def get_region(self):
        return self.diagnosis_keys_export_data.region

    def get_batch_num(self):
        return self.diagnosis_keys_export_data.batch_num

    def get_batch_size(self):
        return self.diagnosis_keys_export_data.batch_size
