import csv
from lib.conversions import *


class RPIEntry:
    def __init__(self, start_time, end_time, rpi, aem, rssi, bdaddr, lat=None, lon=None, altitude=None, speed=None):
        self.start_time = start_time
        self.end_time = end_time
        self.rpi = rpi
        self.aem = aem
        self.rssi = rssi
        self.bdaddr = bdaddr
        self.lat = lat
        self.lon = lon
        self.altitude = altitude
        self.speed = speed


class ScannedRPIs:
    def __init__(self, file_name):
        self.rpis_dict = dict()
        with open(file_name, newline='') as rpi_file:
            rpi_reader = csv.reader(rpi_file, delimiter=';')
            # StartTime, EndTime, RPI, AEM, MaxRSSI, BDADDR [, LAT, LON, Altitude, Speed]
            for row in rpi_reader:
                if row[0] == "StartTime":
                    continue
                if len(row) == 6:
                    rpi = RPIEntry(get_datetime_from_utc_timestamp(int(row[0])),
                                   get_datetime_from_utc_timestamp(int(row[1])),
                                   bytes.fromhex(row[2]), bytes.fromhex(row[3]),
                                   int(row[4]), row[5])
                elif len(row) == 10:
                    rpi = RPIEntry(get_datetime_from_utc_timestamp(int(row[0])),
                                   get_datetime_from_utc_timestamp(int(row[1])),
                                   bytes.fromhex(row[2]), bytes.fromhex(row[3]),
                                   int(row[4]), row[5],
                                   lat=row[6], lon=row[7], altitude=row[8], speed=row[9])
                else:
                    print("ERROR: %s must have only rows with 6 or 10 entries, found a row with %d entries" %
                          (file_name, len(row)))
                    exit(1)
                if rpi.rpi in self.rpis_dict:
                    existing_entries = self.rpis_dict[rpi.rpi]
                    existing_entries.append(rpi)
                    self.rpis_dict[rpi.rpi] = existing_entries
                else:
                    self.rpis_dict[rpi.rpi] = [rpi]
        # print(self.rpis_dict)
