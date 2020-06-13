import struct


class RPIinLevelDB:
    def __init__(self, db):
        self.rpis_dict = dict()
        for key, value in db:
            # each "key" entry has 18 bytes: 2 bytes "day" and 16 bytes "rpi"
            day, rpi = struct.unpack(">H16s", key)
            self.rpis_dict[rpi] = day
        # print(self.rpis_dict)
