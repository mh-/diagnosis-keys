from Crypto.Protocol.KDF import HKDF
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
import struct

interval_length_minutes = 10
tek_rolling_period=144


def en_interval_number(timestamp_seconds):
    return timestamp_seconds // (60 * interval_length_minutes)


def encoded_en_interval_number(enin):
    return struct.pack("<I", enin)


def derive_rpi_key(tek):
    return HKDF(master=tek, key_len=16, salt=None, hashmod=SHA256, context="EN-RPIK".encode("UTF-8"))


def derive_aem_key(tek):
    return HKDF(master=tek, key_len=16, salt=None, hashmod=SHA256, context="EN-AEMK".encode("UTF-8"))


def encrypt_rpi(rpi_key, interval_number):
    enin = encoded_en_interval_number(interval_number)
    padded_data = "EN-RPI".encode("UTF-8") + bytes([0x00] * 6) + enin
    cipher = AES.new(rpi_key, AES.MODE_ECB)
    return cipher.encrypt(padded_data)


def get_rpis(rpi_key, interval_number, interval_count):
    rpis = []
    cipher = AES.new(rpi_key, AES.MODE_ECB)
    padded_data_template = "EN-RPI".encode("UTF-8") + bytes([0x00] * 6)
    for interval in range(interval_number, interval_number+interval_count):
        rpis.append(cipher.encrypt(padded_data_template + encoded_en_interval_number(interval)))
    return rpis


def decrypt_aem(aem_key, aem, rpi):
    cipher = AES.new(aem_key, AES.MODE_CTR, nonce=bytes(0), initial_value=rpi)
    return cipher.decrypt(bytes(aem))
