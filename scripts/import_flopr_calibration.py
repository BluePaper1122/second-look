"""Reproduce a real instrument-data compatibility case from a pinned source.

This imports calibration observations, not a biological validation benchmark.
It never infers assay-control roles from a calibrant's concentration.
"""
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import sys
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from assay import REQUIRED, parse_csv, inspect
from workflow import decision_summary
from transport import tls_context

COMMIT='83d7b92c50a5e12ed692459e5d57d65d08c11665'
SOURCE='examples/plate_reader/tecan_spark/191219_calibration_membrane_parsed.csv'
BLOBS={SOURCE:'815e313821249603bc73a5e6046a0294bf34b383', 'LICENSE':'f288702d2fa16d3cdf0035b15a9fcbc552cd88e7'}
BASE='https://raw.githubusercontent.com/ucl-cssb/flopr/'+COMMIT+'/'


def fetch(path):
    with urllib.request.urlopen(BASE+path,timeout=20,context=tls_context()) as response:
        content=response.read(1_000_001)
    if len(content)>1_000_000:raise ValueError('Upstream source exceeded the expected size.')
    blob=hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
    if blob!=BLOBS[path]:raise ValueError('Upstream bytes did not match the pinned Git blob; no case was created.')
    return content


def convert(content):
    reader=csv.DictReader(io.StringIO(content.decode('utf-8-sig')))
    required={'calibrant','fluorophore','media','concentration','replicate','well','GFP 40'}
    if not required.issubset(reader.fieldnames or []):raise ValueError('The upstream column schema is not supported.')
    converted=[];omitted=[]
    for row in reader:
        if row['calibrant']!='fluorescein':
            omitted.append({'well':row['well'],'reason':'different calibrant'})
            continue
        try:value=float(row['GFP 40'])
        except ValueError:
            omitted.append({'well':row['well'],'reason':'missing/non-numeric GFP 40'})
            continue
        if not math.isfinite(value):
            omitted.append({'well':row['well'],'reason':'non-finite GFP 40'})
            continue
        sid='|'.join(row[k] for k in ('calibrant','fluorophore','media','concentration'))
        converted.append({'plate_id':'flopr_calibration_GFP40','well':row['well'],'sample_id':sid,'value':value,'control':'sample'})
    output=io.StringIO();writer=csv.DictWriter(output,fieldnames=REQUIRED)
    writer.writeheader();writer.writerows(converted)
    return output.getvalue(),omitted


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/'examples'/'flopr-calibration')
    args=parser.parse_args()
    try:
        original=fetch(SOURCE);license_bytes=fetch('LICENSE')
        text,omitted=convert(original)
        rows=parse_csv(text);report=inspect(rows)
        codes={f['code'] for f in report['findings']}
        original_rows=list(csv.DictReader(io.StringIO(original.decode('utf-8-sig'))))
        source_values={r['well'][0]+r['well'][1:].zfill(2):float(r['GFP 40']) for r in original_rows if r['calibrant']=='fluorescein' and r['GFP 40']!='NA'}
        checks={'source_measurements_preserved':{r['well']:r['value'] for r in rows}==source_values,
                'control_roles_not_invented':all(r['control']=='sample' for r in rows),
                'control_requirement_disclosed':'controls' in codes,
                'control_score_withheld':'z_prime' not in report['facts'],
                'finite_report':True}
        json.dumps(report,allow_nan=False)
        if not all(checks.values()):raise ValueError('External compatibility expectations did not hold.')
        provenance={'kind':'real instrument calibration compatibility case; not biological validation',
                    'source_repository':'https://github.com/ucl-cssb/flopr','source_commit':COMMIT,
                    'source_url':BASE+SOURCE,'source_blob_sha1':BLOBS[SOURCE],
                    'source_sha256':hashlib.sha256(original).hexdigest(),
                    'converted_sha256':hashlib.sha256(text.encode()).hexdigest(),
                    'upstream_license':'GPL-3.0; retained separately from Second Look MIT source code',
                    'channel':'GFP 40; raw arbitrary instrument units as provided upstream',
                    'selection':'fluorescein calibrant rows with finite numeric GFP 40 values',
                    'sample_identity_fields':['calibrant','fluorophore','media','concentration'],
                    'role_mapping':'all imported rows are sample; no assay positive/negative roles are inferred',
                    'measured_wells':len(rows),'omitted_rows':omitted,
                    'checks':checks,'finding_codes':sorted(codes),
                    'report_id':decision_summary(report,rows)['report_id'],
                    'limitations':['Only one calibration channel is imported; no kinetics or normalization is performed.',
                                   'A concentration gradient is intentional and must not be interpreted as proof of an edge artifact.',
                                   'This case checks compatibility and abstention, not sensitivity/specificity, biological validity, or model quality.']}
        args.output.mkdir(parents=True,exist_ok=True)
        (args.output/'upstream_calibration.csv').write_bytes(original)
        (args.output/'LICENSE.GPL-3.0').write_bytes(license_bytes)
        (args.output/'plate.csv').write_text(text)
        (args.output/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
        print(json.dumps({k:provenance[k] for k in ('kind','measured_wells','checks','finding_codes','report_id')},indent=2))
    except (OSError,ValueError,urllib.error.URLError) as e:
        print('Import failed: '+str(e),file=sys.stderr)
        return 1
    return 0

if __name__=='__main__':raise SystemExit(main())
