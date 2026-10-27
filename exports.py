"""Recompute export contents and preserve source identity and review boundaries."""
from datetime import datetime,timezone
import hashlib
import json
from assay import plan,csv_export
from errors import AppError
from workflow import ANALYSIS_VERSION,decision_summary


def prepare_plan(rows,report,data):
    ids=data.get('samples')
    if not isinstance(ids,list) or any(not isinstance(s,str) or s not in report['samples'] for s in ids):
        raise AppError('unknown_sample','Select sample IDs from the currently inspected plate.')
    controls=data.get('controls')
    if not isinstance(controls,dict) or any(not isinstance(controls.get(role),str) or controls[role] not in report['control_ids'][role] for role in ('negative','positive')):
        raise AppError('control_selection','Choose a measured negative and positive control material from this plate. If the control information is missing, correct the input before designing the follow-up.')
    result=plan(ids,data.get('budget'),data.get('seed',11),controls)
    source_id=decision_summary(report,rows)['report_id']
    identity={'source_report_id':source_id,'rows':result['rows'],'budget':result['budget'],'seed':result['seed']}
    layout_id=hashlib.sha256(json.dumps(identity,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:16]
    return {**result,'csv':csv_export(result['rows']),'source_report_id':source_id,'layout_id':layout_id}


def reviewed_plan(rows,report,data):
    if data.get('reviewed') is not True:
        raise AppError('review_required','Review the proposed layout for assay compatibility before exporting it.')
    result=prepare_plan(rows,report,data)
    if data.get('source_report_id')!=result['source_report_id'] or data.get('layout_id')!=result['layout_id']:
        raise AppError('stale_layout','The source measurements or follow-up settings have changed. Generate and review the updated layout before exporting.',409)
    exported_at=datetime.now(timezone.utc).isoformat()
    exported_rows=[{**row,'source_report_id':result['source_report_id'],'layout_id':result['layout_id'],
                    'analysis_version':ANALYSIS_VERSION,'randomization_seed':result['seed'],'well_budget':result['budget'],
                    'review_status':'researcher_attested','exported_at_utc':exported_at} for row in result['rows']]
    return {**result,'csv':csv_export(exported_rows),'exported_at_utc':exported_at,
            'review_notice':'Review is an explicit user attestation. Reviewer identity, expertise, and assay validity are not verified.'}


def handoff(rows,report,data):
    notes=data.get('notes','');provenance=data.get('provenance','Source attribution not supplied')
    if not isinstance(notes,str) or len(notes)>10000:
        raise AppError('export_notes','Researcher notes must be plain text with at most 10,000 characters.')
    if not isinstance(provenance,str) or len(provenance)>1000:
        raise AppError('export_provenance','Source attribution must be text with at most 1,000 characters.')
    for key in ('include_layout','layout_present'):
        if type(data.get(key,False)) is not bool:raise AppError('export_options','Choose valid handoff export options.')
    workflow=decision_summary(report,rows)
    lines=['SECOND LOOK — RESEARCH HANDOFF',
           'Source attribution supplied by the client (not independently verified):',
           '  '+''.join(c if c.isprintable() else ' ' for c in provenance),
           'Report: '+workflow['report_id']+' | Analysis version: '+ANALYSIS_VERSION,
           'This export contains deterministic observations and researcher notes. A language-model review is not included.',
           '',report['scope'],'','REVIEW GUIDANCE',workflow['message'],workflow['decision_boundary']]
    for action in workflow['actions']:lines.extend([action['title'],action['detail']])
    lines.extend(['','OBSERVATIONS'])
    for finding in report['findings']:
        lines.extend([finding['title'],finding['detail']])
        for ref in finding['evidence']:lines.append(ref+': '+json.dumps(report['facts'][ref],ensure_ascii=False))
        lines.append('')
    lines.extend(['RESEARCHER NOTES — USER-SUPPLIED, NOT MODEL FINDINGS'])
    lines.extend('  | '+line for line in notes.splitlines())
    if not notes:lines.append('  | No researcher notes supplied.')
    lines.extend(['','REPEATED MEASUREMENTS BY POSITION'])
    for summary in report['replicate_summaries']:
        lines.append(summary['sample_id']+' | '+summary['role']+' | '+summary['zone'])
        for ref in summary['evidence']:lines.append(ref+': '+json.dumps(report['facts'][ref],ensure_ascii=False))
    lines.extend(['','LIMITS','Spatial associations do not establish causation. Technical wells do not establish biological replication. Compatibility and synthetic integrity checks do not establish scientific validity.'])
    included=False
    if data.get('include_layout'):
        result=reviewed_plan(rows,report,data)
        lines.extend(['','REVIEWED FOLLOW-UP PROPOSAL','Layout: '+result['layout_id'],
                      'Source report: '+result['source_report_id'],'Exported at UTC: '+result['exported_at_utc'],
                      result['review_notice'],result['explanation'],result['csv']])
        included=True
    elif data.get('layout_present'):
        lines.extend(['','UNREVIEWED FOLLOW-UP DRAFT','A draft exists in the application. Its well assignments were omitted because review was not attested. Review the current layout before exporting those assignments.'])
    else:
        lines.extend(['','NEXT STEP','Select samples and generate a follow-up layout for human review if appropriate to the assay.'])
    return {'text':'\n'.join(lines)+'\n','source_report_id':workflow['report_id'],'includes_reviewed_layout':included,
            'filename':'second-look-'+workflow['report_id']+'-handoff.txt'}
