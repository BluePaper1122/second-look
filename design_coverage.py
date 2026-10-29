"""Observed versus proposed position coverage, without predicting outcomes."""
from assay import edge


def position_coverage(observed, proposed, samples, controls):
    materials=[]
    for role, sample_id in [('sample',s) for s in sorted(samples)]+[(role,controls[role]) for role in ('negative','positive')]:
        def zones(rows):
            selected=[r for r in rows if r['sample_id']==sample_id and r['control']==role]
            return {zone:[r['well'] for r in selected if edge(r['well'])==flag]
                    for zone,flag in (('edge',True),('interior',False))}
        before,after=zones(observed),zones(proposed)
        materials.append({'sample_id':sample_id,'role':role,
                          'observed':{z:len(wells) for z,wells in before.items()},
                          'proposed':{z:len(wells) for z,wells in after.items()},
                          'observed_wells':before,'proposed_wells':after,
                          'previously_crossed':all(before.values()),'proposed_crossed':all(after.values())})
    selected=[m for m in materials if m['role']=='sample']
    gained=sum(not m['previously_crossed'] and m['proposed_crossed'] for m in selected)
    return {'materials':materials,'selected_sample_count':len(selected),'samples_gaining_coverage':gained,
            'summary':f'This proposal adds the missing position zone for {gained} of {len(selected)} selected sample IDs.' if gained else 'The selected sample IDs already occur in both position zones. This proposal adds a defined, balanced technical-repeat template.',
            'question':'Does each selected material occur at both edge and interior positions?',
            'limits':'This checks layout coverage only. Proposed wells have no measured outcomes. Crossing position with identity does not establish biological activity, statistical power, or a causal explanation, and does not balance row, column, batch, or handling factors.'}
