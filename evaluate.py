"""Held-out synthetic integrity checks. Not a scientific accuracy benchmark."""
from collections import Counter
import json
from pathlib import Path
from assay import example, parse_csv, inspect, edge
from errors import AppError
from exports import prepare_plan


def main():
    results = []
    for kind in ('clean','artifact','biology','both','confounded','missing_controls','inconsistent'):
        for seed in range(100, 120):
            rows = parse_csv(example(kind, seed))
            report = inspect(rows)
            codes = {f['code'] for f in report['findings']}
            checks = {
                'finite_serializable_report': True,
                'evidence_references_resolve': all(e in report['facts'] for f in report['findings'] + report['replicate_summaries'] for e in f['evidence']),
            }
            json.dumps(report, allow_nan=False)
            if kind == 'confounded': checks['confounding_disclosed'] = 'confounding' in codes
            if kind == 'missing_controls': checks['missing_controls_disclosed'] = 'controls' in codes
            samples = report['samples'][:2]
            controls = {role: next(iter(report['control_ids'][role]), '') for role in ('negative','positive')}
            settings = {'samples': samples, 'budget': 24, 'seed': seed, 'controls': controls}
            if any(not value for value in controls.values()):
                try:
                    prepare_plan(rows, report, settings)
                except AppError as error:
                    checks['missing_controls_block_allocation'] = error.code == 'control_selection'
                else:
                    checks['missing_controls_block_allocation'] = False
            else:
                layout = prepare_plan(rows, report, settings)
                allocations = layout['rows']
                counts = Counter((r['sample_id'], 'edge' if edge(r['well']) else 'interior') for r in allocations)
                materials = samples + list(controls.values())
                expected = Counter({(material, zone): 2 for material in materials for zone in ('edge','interior')})
                checks.update({
                    'budget_observed': len(allocations) <= settings['budget'],
                    'unique_wells': len({r['well'] for r in allocations}) == len(allocations),
                    'only_selected_materials_and_balanced_zones': counts == expected,
                    'exact_template_well_count': len(allocations) == 4 * len(samples) + 8,
                    'measured_control_roles_preserved': all(r['control'] == next((role for role, material in controls.items() if r['sample_id'] == material), 'sample') for r in allocations),
                    'selection_order_invariant': prepare_plan(rows, report, {**settings, 'samples': list(reversed(samples))})['layout_id'] == layout['layout_id'],
                })
            results.append({'scenario': kind, 'seed': seed, 'checks': checks, 'passed': all(checks.values())})
    summary = {
        'scope': 'Synthetic integrity checks only; does not measure artifact detection accuracy, biological validity, or live model quality.',
        'allocation_scope': 'Uses the product allocation validation path; missing controls must block allocation. Feasible layouts are checked independently for selected materials, measured roles, two wells per zone, unique positions, budget, and selection-order invariance.',
        'cases': len(results), 'passed': sum(r['passed'] for r in results),
        'failed': [r for r in results if not r['passed']], 'development_seed': 11,
        'held_out_seeds': '100–119', 'results': results,
    }
    Path('docs/evaluation.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k != 'results'}, indent=2))
    if summary['failed']: raise SystemExit(1)


if __name__ == '__main__': main()
