# diagnosis-keys
Tools for working with Diagnosis Keys from the COVID-19 Exposure Notification / Corona-Warn-App system

## Installation
    % git clone https://github.com/mh-/diagnosis-keys
    $ cd diagnosis-keys
    $ pip3 install -r requirements.txt

## Use
```
% ./parse_keys.py -d testExport-2-records-1-of-1.zip
Exposure Notification Diagnosis Key Parser
This script parses published Diagnosis Keys.

File 'testExport-2-records-1-of-1.zip' read.
- Time window: 2020-05-22 17:00:00 CEST - 2020-05-23 17:00:00 CEST
- Region: US
- Batch: 1 of 1
- Signature Info:
verification_key_version: "1"
verification_key_id: "some_id"
signature_algorithm: "1.2.840.10045.4.3.2"

TEKs:
  1: TEK: 172fc480e598490c34177604339b1543, Transmission Risk Level: 8, Time: 2020-05-20 17:20:00 CEST - 2020-05-20 17:30:00 CEST (2649980, 1)
  2: TEK: 2b63053ac483238de176169e861f3dcd, Transmission Risk Level: 1, Time: 2020-05-19 22:20:00 CEST - 2020-05-20 17:20:00 CEST (2649866, 114)
```

You can download an example Diagnosis Keys file here:
https://github.com/google/exposure-notifications-server/blob/master/examples/export/testExport-2-records-1-of-1.zip
(This file was generated from https://github.com/google/exposure-notifications-server/blob/master/examples/export/keys.json, 
using Google's [export-generate](https://github.com/google/exposure-notifications-server/tree/master/examples/export) tool.)
