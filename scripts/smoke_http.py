"""Synthetic-only serving check. Never calls a model or reads private assay files."""
import argparse
import csv
import io
import json
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from assay import example
from transport import tls_context


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--url',default='http://127.0.0.1:8088')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--timeout',type=float,default=8,help='Per-request seconds (1–120). Use 90 for an idle Free Render instance; no automatic retries.')
    args=parser.parse_args()
    if not 1<=args.timeout<=120:parser.error('--timeout must be from 1 to 120 seconds.')
    origin=args.url.rstrip('/')
    parts=urllib.parse.urlsplit(origin)
    if parts.username or parts.password or parts.path or parts.query or parts.fragment or (parts.scheme!='https' and not(parts.scheme=='http' and parts.hostname in ('localhost','127.0.0.1'))):
        raise SystemExit('Use an HTTPS origin, or a localhost HTTP origin, without credentials or a path.')
    def request(path,method='GET',payload=None,extra_headers=None):
        body=json.dumps(payload).encode() if payload is not None else None
        headers={'Content-Type':'application/json'};headers.update(extra_headers or {})
        req=urllib.request.Request(origin+path,data=body,headers=headers,method=method)
        try:response=urllib.request.urlopen(req,timeout=args.timeout,context=tls_context())
        except urllib.error.HTTPError as e:response=e
        with response:
            raw=response.read(1_500_001)
            if len(raw)>1_500_000:raise ValueError('Response exceeds supported size.')
            return response.code,response.headers,raw
    try:
        status,headers,raw=request('/api/status')
        health=json.loads(raw)
        head_status,_,head_body=request('/',method='HEAD')
        inspect_status,inspect_headers,raw=request('/api/inspect','POST',{'csv':example()},{'Origin':origin})
        report=json.loads(raw)
        denied_status,_,raw=request('/api/inspect','POST',{}, {'Origin':'https://cross-origin.invalid'})
        denied=json.loads(raw)
        checks={'health_responds':status==200,
                'head_without_body':head_status==200 and head_body==b'',
                'synthetic_plate_inspected':inspect_status==200 and len(report.get('rows',[]))==96,
                'cross_origin_rejected':denied_status==403 and denied.get('code')=='cross_origin',
                'security_headers_present':all(inspect_headers.get(name) for name in ('Content-Security-Policy','Cache-Control','Referrer-Policy','X-Request-ID'))}
        settings={'csv':example(),'samples':['candidate_edge','candidate_interior'],
                  'controls':{'negative':'negative_control','positive':'positive_control'},'budget':24,'seed':11}
        plan_status,_,raw=request('/api/plan','POST',settings,{'Origin':origin})
        layout=json.loads(raw)
        review={**settings,'source_report_id':layout.get('source_report_id'),'layout_id':layout.get('layout_id'),'reviewed':True}
        blocked_status,_,raw=request('/api/export-plan','POST',{**review,'reviewed':False},{'Origin':origin})
        blocked=json.loads(raw)
        export_status,_,raw=request('/api/export-plan','POST',review,{'Origin':origin})
        exported=json.loads(raw)
        allocations=list(csv.DictReader(io.StringIO(exported.get('csv',''))))
        handoff_status,_,raw=request('/api/export-handoff','POST',{**settings,'layout_present':True},{'Origin':origin})
        handoff=json.loads(raw)
        stale_status,_,raw=request('/api/export-plan','POST',{**review,'seed':12},{'Origin':origin})
        stale=json.loads(raw)
        checks.update({
            'synthetic_layout_allocated':plan_status==200 and layout.get('used')==16,
            'unreviewed_export_rejected':blocked_status==400 and blocked.get('code')=='review_required',
            'reviewed_csv_received_and_parsed':export_status==200 and len(allocations)==16,
            'export_metadata_preserved':bool(allocations) and all(
                row.get('source_report_id')==layout.get('source_report_id') and row.get('layout_id')==layout.get('layout_id')
                and row.get('review_status')=='researcher_attested' and row.get('randomization_seed')=='11'
                and row.get('well_budget')=='24' and bool(row.get('exported_at_utc')) for row in allocations),
            'unreviewed_handoff_assignments_omitted':handoff_status==200 and handoff.get('includes_reviewed_layout') is False
                and 'UNREVIEWED FOLLOW-UP DRAFT' in handoff.get('text','') and 'technical_replicate' not in handoff.get('text',''),
            'stale_export_rejected':stale_status==409 and stale.get('code')=='stale_layout',
        })
        result={'origin':origin,'request_timeout_seconds':args.timeout,'checks':checks,'passed':all(checks.values()),'model_configured':bool(health.get('model_configured')),
                'live_model_calls':0,'scope':'HTTP serving and synthetic data flow at the recorded origin only; does not establish ongoing availability, live-model quality, load capacity, a security audit, or biological validity.'}
    except (OSError,ValueError,KeyError,urllib.error.URLError):
        result={'origin':origin,'request_timeout_seconds':args.timeout,'passed':False,'live_model_calls':0,'message':'The serving check could not complete. Confirm the process, configured origin and port, and retry.'}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return 0 if result['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
