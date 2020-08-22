# diagnosis-keys
Tools for working with Diagnosis Keys from the COVID-19 Exposure Notification / Corona-Warn-App system

    Copyright (C) 2020  Michael Huebler and other contributors

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

## Installation
    % git clone https://github.com/mh-/diagnosis-keys
    % cd diagnosis-keys
    % pip3 install -r requirements.txt

## Use
```
% ./parse_keys.py -d testExport-2-records-1-of-1.zip                              
Exposure Notification Diagnosis Key Parser
This script parses published Diagnosis Keys.

File 'testExport-2-records-1-of-1.zip' read.
- Time window: 2020-05-22 15:00:00 UTC - 2020-05-23 15:00:00 UTC
- Region: US
- Batch: 1 of 1
- Signature Info:
verification_key_version: "1"
verification_key_id: "some_id"
signature_algorithm: "1.2.840.10045.4.3.2"

Diagnosis Keys:
  1: TEK: 172fc480e598490c34177604339b1543, Transmission Risk Level: 8, Validity: 2020-05-20 15:20:00 UTC - 2020-05-20 15:30:00 UTC (2649980, 1)
  2: TEK: 2b63053ac483238de176169e861f3dcd, Transmission Risk Level: 1, Validity: 2020-05-19 20:20:00 UTC - 2020-05-20 15:20:00 UTC (2649866, 114)
```

You can download an example Diagnosis Keys file here:
https://github.com/google/exposure-notifications-server/blob/master/examples/export/testExport-2-records-1-of-1.zip
(This file was generated from https://github.com/google/exposure-notifications-server/blob/master/examples/export/keys.json, 
using Google's [export-generate](https://github.com/google/exposure-notifications-server/tree/master/examples/export) tool.)

Another example run:
```
% ./parse_keys.py -c app_contact-tracing-contact-record-db/ -d tekExport.zip -l -s
Exposure Notification Diagnosis Key Parser
This script parses published Diagnosis Keys.

File 'tekExport.zip' read.
- Time window: 2020-06-12 13:25:31 CEST - 2020-06-13 13:25:31 CEST
- Region: US
- Batch: 1 of 1
- Signature Info:
verification_key_version: "1"
verification_key_id: "some_id"
signature_algorithm: "1.2.840.10045.4.3.2"

Diagnosis Keys:
  1: TEK: b534b9654ba21dcd60a9b3e17d620443, Transmission Risk Level: 5, Validity: 2020-06-13 02:00:00 CEST - 2020-06-14 02:00:00 CEST (2653344, 144)
FOUND MATCH!
RPI Validity: 2020-06-13 12:40:00 CEST - 2020-06-13 12:50:00 CEST (Interval number: 2653408, RPI: 1b013a80678747f73b140e8e3e46a3aa)
2020-06-13 12:44:12 CEST Attenuation: 43dB (RSSI: -57dBm, AEM: 919c3296, Metadata: 40f20000)
(...)
FOUND MATCH!
RPI Validity: 2020-06-13 12:50:00 CEST - 2020-06-13 13:00:00 CEST (Interval number: 2653409, RPI: 99b8e671e0759ca9532a25ea3f992a8b)
2020-06-13 12:54:41 CEST Attenuation: 34dB (RSSI: -58dBm, AEM: 36563b98, Metadata: 40e80000)
(...)
FOUND MATCH!
RPI Validity: 2020-06-13 13:00:00 CEST - 2020-06-13 13:10:00 CEST (Interval number: 2653410, RPI: f357370f15be3f7ec06030ca34899223)
2020-06-13 13:07:20 CEST Attenuation: 34dB (RSSI: -58dBm, AEM: 9be98c37, Metadata: 40e80000)
(...)
```

## Used by
This tool is used by a number of CWA diagnosis key visualisation projects such as:

- https://ctt.pfstr.de/
- https://micb25.github.io/dka/

