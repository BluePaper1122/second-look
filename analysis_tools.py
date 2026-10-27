"""Read-only, explicitly scoped analyses an agent may request.

These tools calculate descriptive evidence, never biological hit rankings or
experimental actions. Calls cannot change the uploaded data or selected samples.
"""
import math
import statistics as st
from assay import edge
from errors import AppError

CATALOG = {
    'control_pair': 'Compare the researcher-selected positive and negative control materials. No pooling across identities.',
    'sample_position': 'Describe one selected sample at edge and interior positions, with exact supporting wells.',
    'design_feasibility': 'Calculate the well requirement for the researcher-selected samples and controls; never change selections.',
}


def zone_summary(rows):
    result = {}
    for flag, label in ((True,'edge'),(False,'interior')):
        selected = [r for r in rows if edge(r['well']) == flag]
        values = [r['value'] for r in selected]
        result[label] = {'count':len(values),'mean':st.mean(values) if values else None,
                         'sd':st.stdev(values) if len(values)>1 else None,
                         'wells':[r['well'] for r in selected]}
    return result


def execute_tool(call, rows, settings):
    if not isinstance(call,dict) or set(call) != {'name','arguments'} or call.get('name') not in CATALOG or not isinstance(call.get('arguments'),dict):
        raise AppError('agent_tool_invalid','The model requested an unsupported analysis. No model result was accepted.',502,True)
    name, args = call['name'], call['arguments']
    if name == 'sample_position':
        if set(args) != {'sample_id'} or not isinstance(args['sample_id'],str) or args['sample_id'] not in settings['samples']:
            raise AppError('agent_scope_invalid','The model requested a sample outside your selection. The request was rejected.',502,True)
        sample = [r for r in rows if r['control']=='sample' and r['sample_id']==args['sample_id']]
        summary = zone_summary(sample)
        e,i=summary['edge'],summary['interior']
        crossed = bool(e['count'] and i['count'])
        return {'name':name,'title':'Position measurements: '+args['sample_id'],'status':'available' if crossed else 'needs_data',
                'values':summary,'edge_minus_interior':e['mean']-i['mean'] if crossed else None,
                'explanation':'The same selected sample is measured in both position zones. The difference is descriptive and may reflect other factors.' if crossed else 'This selected sample occurs in only one position zone. Its measurements cannot separate sample identity from position.',
                'limitations':'Technical wells do not establish biological replication. No statistical significance or causal conclusion is calculated.'}
    if name == 'control_pair':
        if args:
            raise AppError('agent_tool_invalid','The control analysis must use your selected materials without replacing them.',502,True)
        controls=settings['controls']
        selected={role:[r for r in rows if r['control']==role and r['sample_id']==controls.get(role)] for role in ('negative','positive')}
        if not all(controls.get(role) and selected[role] for role in selected):
            return {'name':name,'title':'Selected control pair','status':'needs_selection','values':{},'explanation':'Select one measured negative and positive control material before a pair-specific analysis.','limitations':'The model cannot choose substitute control materials on your behalf.'}
        values={role:{'sample_id':controls[role],**zone_summary(rs)} for role,rs in selected.items()}
        z=None
        reason='At least two measurements of each selected control are needed for a pair-specific Z-prime.'
        if all(len(rs)>=2 for rs in selected.values()):
            p,n=([r['value'] for r in selected[role]] for role in ('positive','negative'))
            difference=abs(st.mean(p)-st.mean(n))
            if difference:
                candidate=1-3*(st.stdev(p)+st.stdev(n))/difference
                z=candidate if math.isfinite(candidate) else None
                reason='Z-prime uses only the selected pair; other control identities are excluded.' if z is not None else 'A finite control score cannot be represented for this pair.'
            else:
                reason='The selected control means coincide; Z-prime is undefined.'
        return {'name':name,'title':'Selected control pair','status':'available' if z is not None else 'needs_data','values':values,'z_prime':z,'explanation':reason,'limitations':'The score does not establish assay validity. Position summaries remain descriptive.'}
    if args:
        raise AppError('agent_tool_invalid','The feasibility analysis must use your current follow-up settings.',502,True)
    count=len(settings['samples']); needed=4*count+8
    valid_controls=all(any(r['control']==role and r['sample_id']==settings['controls'].get(role) for r in rows) for role in ('negative','positive'))
    feasible=count>0 and count<=16 and valid_controls and needed<=settings['budget']
    return {'name':name,'title':'Follow-up feasibility','status':'available' if feasible else 'needs_settings',
            'values':{'selected_sample_count':count,'required_wells':needed,'budget':settings['budget'],'selected_controls_present':valid_controls},
            'explanation':'Your selected materials fit the current position-check design.' if feasible else 'The current design needs at least one selected sample, identified controls, sufficient budget, and at most sixteen samples.',
            'limitations':'This checks the defined design template, not optimal allocation or biological power. No sample is added or removed and no experiment is scheduled.'}
