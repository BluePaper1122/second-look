"""Synthetic-only serving check. Never calls a model or reads private assay files."""
import argparse
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
    args=parser.parse_args()
    origin=args.url.rstrip('/')
    parts=urllib.parse.urlsplit(origin)
    if parts.username or parts.password or parts.path or parts.query or parts.fragment or (parts.scheme!='https' and not(parts.scheme=='http' and parts.hostname in ('localhost','127.0.0.1'))):
        raise SystemExit('Use an HTTPS origin, or a localhost HTTP origin, without credentials or a path.')
    def request(path,method='GET',payload=None,extra_headers=None):
        body=json.dumps(payload).encode() if payload is not None else None
        headers={'Content-Type':'application/json'};headers.update(extra_headers or {})
        req=urllib.request.Request(origin+path,data=body,headers=headers,method=method)
        try:response=urllib.request.urlopen(req,timeout=8,context=tls_context())
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
        result={'origin':origin,'checks':checks,'passed':all(checks.values()),'model_configured':bool(health.get('model_configured')),
                'live_model_calls':0,'scope':'HTTP serving and local data flow only; not a public deployment, live-model, load, security-audit, or biological validation claim.'}
    except (OSError,ValueError,KeyError,urllib.error.URLError):
        result={'origin':origin,'passed':False,'live_model_calls':0,'message':'The serving check could not complete. Confirm the process, configured origin and port, and retry.'}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return 0 if result['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
