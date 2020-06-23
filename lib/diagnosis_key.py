class DiagnosisKey:
    def __init__(self, key_bytes, start_interval, validity_period, transmission_risk_level):
        self.key_bytes = key_bytes
        self.start_interval = start_interval
        self.validity_period = validity_period
        self.transmission_risk_level = transmission_risk_level
