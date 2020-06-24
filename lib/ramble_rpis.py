import sqlite3
from lib.conversions import get_datetime_from_utc_timestamp
from lib.scanned_rpis import RPIEntry


class RambleRPIs:

    __ramble_sql_script= \
    """
        SELECT
            locations.timestamp as 'timestamp_start',
            locations.timestamp as 'timestamp_end',
            devices.service_data as 'identifier',
            locations.rssi as 'rssi',
            devices.id as 'device_id',
            locations.latitude as 'lat',
            locations.longitude as 'long'
        FROM
            devices
        INNER JOIN locations ON devices.id = locations.device_id
        WHERE
             devices.service_data LIKE 'fd6f:%'
        ORDER BY
            devices.id, locations.timestamp;
    """

    def __init__(self, file_name):
        self.rpis_dict = dict()
        with sqlite3.connect(file_name) as db_conn:
            rpi_reader = db_conn.execute(RambleRPIs.__ramble_sql_script)
            # StartTime, EndTime, RPI, AEM, MaxRSSI, BDADDR [, LAT, LON, Altitude, Speed]
            full_rpi_list = rpi_reader.fetchall()
            rpi_list = []
            # get start and end date from multiple rows
            for c_row, row in enumerate(full_rpi_list):
                if (c_row > 0) and (row[4] == full_rpi_list[c_row-1][4]):
                    rpi_list[-1][1] = row[1] # replace end date with later timestamp
                    if rpi_list[-1][3] < row[3]: #replace stronger RSSI
                        rpi_list[-1][3] = row[3]
                else:
                    rpi_list.append(list(row)) # first entry for this ID, create it

            for row in rpi_list:
                rpi_value = row[2][5:37]
                aem_value = row[2][37:]
                rpi = RPIEntry(get_datetime_from_utc_timestamp(int(row[0])),
                               get_datetime_from_utc_timestamp(int(row[1])),
                               bytes.fromhex(rpi_value), bytes.fromhex(aem_value),
                               int(row[3]), row[4],
                               lat=row[5], lon=row[6])

                if rpi.rpi in self.rpis_dict:
                    existing_entries = self.rpis_dict[rpi.rpi]
                    existing_entries.append(rpi)
                    self.rpis_dict[rpi.rpi] = existing_entries
                else:
                    self.rpis_dict[rpi.rpi] = [rpi]

        # print('Recorded %d unique RPIs' % len(self.rpis_dict))