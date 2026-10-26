"""Held-out synthetic integrity checks. Not a scientific accuracy benchmark."""
import json
from pathlib import Path
from assay import example, parse_csv, inspect, plan, edge

def main():
    results = []
    for kind in ('clean','artifact','biology','both','confounded','missing_controls','inconsistent'):
        for seed in range(100, 120):
            report = inspect(parse_csv(example(kind, seed)))
            codes = {f['code'] for f in report['findings']}
            checks = {'finite_serializable_report': True, 'evidence_references_resolve': all(e in report['facts'] for f in report['findings'] for e in f['evidence'])}
            if kind == 'confounded': checks['confounding_disclosed'] = 'confounding' in codes
            if kind == 'missing_controls': checks['missing_controls_disclosed'] = 'controls' in codes
            layout = plan(report['samples'][:2],24,seed)
            checks['budget_observed'] = len(layout['rows']) <= 24
            checks['unique_wells'] = len({r['well'] for r in layout['rows']}) == len(layout['rows'])
            results.append({'scenario':kind,'seed':seed,'checks':checks,'passed':all(checks.values())})
            json.dumps(report,allow_nan=False)
    summary = {'scope':'Synthetic integrity checks only; does not measure artifact detection accuracy, biological validity, or live model quality.', 'cases':len(results), 'passed':sum(r['passed'] for r in results), 'failed':[r for r in results if not r['passed']], 'development_seed':11, 'held_out_seeds':'100–119', 'results':results}
    Path('docs/evaluation.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='results'},indent=2))
    if summary['failed']: raise SystemExit(1)

if __name__=='__main__': main()
