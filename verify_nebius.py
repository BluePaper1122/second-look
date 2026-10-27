"""Explicit synthetic-only runtime verification; never reads private assay files."""
import argparse
import json
import os
from pathlib import Path
from assay import example, parse_csv, inspect
from agent_review import run_review
from errors import AppError
from server import model_json
from local_config import load_local_configuration


def main():
    parser=argparse.ArgumentParser(description='Check configuration, or explicitly run a synthetic two-call NVIDIA/Nebius review.')
    parser.add_argument('--live-review',action='store_true',help='Make two provider inference calls using synthetic data; provider usage may be charged.')
    parser.add_argument('--output',type=Path,help='Write a verification record without credentials or private assay data.')
    args=parser.parse_args()
    try:load_local_configuration()
    except (OSError,ValueError):
        print('Local configuration could not be loaded. Check its permissions or run setup_nebius.py again.')
        return 2
    configured=bool(os.getenv('NEBIUS_API_KEY') and os.getenv('NEBIUS_MODEL'))
    record={'configured':configured,'live_verified':False,'data':'generated synthetic plate only'}
    if not configured:
        record['message']='Configure NEBIUS_API_KEY and NEBIUS_MODEL securely in the server environment. No live call was attempted.'
    elif not args.live_review:
        record['message']='Configuration is present but unverified. Use --live-review to explicitly attempt the synthetic runtime check.'
    else:
        rows=parse_csv(example())
        settings={'samples':['candidate_edge'],'controls':{'negative':'negative_control','positive':'positive_control'},'budget':12}
        try:
            result=run_review(rows,inspect(rows),'position',settings,model_json)
            if result.get('mode')!='live':
                raise AppError('model_unconfigured','A complete live review was not returned.',503)
            record.update({'live_verified':True,'model':result['model'],'source_report_id':result['source_report_id'],
                           'runtime_calls':result['runtime_calls'],'agent_version':result['agent_version'],'analysis_names':[a['name'] for a in result['analyses']],
                           'message':'Two runtime responses passed schema and evidence-reference checks. This does not establish scientific validity or model usefulness.'})
        except AppError as e:
            record.update({'error_code':e.code,'message':str(e)})
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))
    return 0 if record['live_verified'] else 2

if __name__=='__main__':raise SystemExit(main())
