"""Checks a real calibration input without treating it as biological ground truth."""
import csv
import hashlib
import io
import json
from pathlib import Path
import ssl
import unittest
from unittest.mock import Mock, patch
from assay import parse_csv, inspect
from transport import tls_context

ROOT=Path(__file__).resolve().parents[1]

class ExternalCalibrationTests(unittest.TestCase):
    def test_raw_source_has_pinned_identity(self):
        content=(ROOT/'examples/flopr-calibration/upstream_calibration.csv').read_bytes()
        blob=hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
        self.assertEqual(blob,'815e313821249603bc73a5e6046a0294bf34b383')
    def test_converted_measurements_match_source_independently(self):
        source=list(csv.DictReader(io.StringIO((ROOT/'examples/flopr-calibration/upstream_calibration.csv').read_text())))
        expected={r['well'][0]+r['well'][1:].zfill(2):float(r['GFP 40']) for r in source if r['calibrant']=='fluorescein'}
        rows=parse_csv((ROOT/'examples/flopr-calibration/plate.csv').read_text())
        self.assertEqual(len(rows),48)
        self.assertEqual({r['well']:r['value'] for r in rows},expected)
    def test_absent_assay_controls_are_not_fabricated(self):
        rows=parse_csv((ROOT/'examples/flopr-calibration/plate.csv').read_text())
        report=inspect(rows)
        self.assertEqual(report['control_ids'],{'negative':[],'positive':[]})
        self.assertNotIn('z_prime',report['facts'])
        self.assertIn('controls',[f['code'] for f in report['findings']])
        self.assertEqual(report['facts']['matched_id_count']['value'],10)
        self.assertEqual(report['facts']['uncrossed_sample_count']['value'],2)
        json.dumps(report,allow_nan=False)

class TLSConfigurationTests(unittest.TestCase):
    def test_certificate_and_hostname_checks_remain_required(self):
        context=tls_context()
        self.assertEqual(context.verify_mode,ssl.CERT_REQUIRED)
        self.assertTrue(context.check_hostname)
    def test_explicit_trust_configuration_not_overridden(self):
        context=Mock();context.get_ca_certs.return_value=[]
        with patch('transport.ssl.create_default_context',return_value=context),patch.dict('os.environ',{'SSL_CERT_FILE':'explicit-user-path'}):
            self.assertIs(tls_context(),context)
        context.load_verify_locations.assert_not_called()
