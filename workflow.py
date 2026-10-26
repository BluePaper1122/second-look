"""Researcher-facing decisions supported by the deterministic QC report."""
import hashlib
import json

ANALYSIS_VERSION = '0.2.0'
ACTIONS = {
    'controls': ('Confirm the control measurements', 'Check the plate map and control labels. Add the missing control data or repeat with suitable controls before relying on a control separation score.'),
    'mixed_controls': ('Choose one compatible control pair', 'Review the control identities. Keep distinct control materials separate; a pooled quality score is not available for this plate.'),
    'control_overlap': ('Check why the controls overlap', 'Verify control labels, measurement units, and instrument export. If the overlap is genuine, review assay performance before selecting samples for follow-up.'),
    'zprime': ('Review the control separation', 'Inspect the referenced control wells and their variability against your assay’s own acceptance criteria. This app does not decide whether a plate is valid.'),
    'confounding': ('Separate sample and position in a follow-up', 'Select the relevant sample IDs below. The follow-up planner places each selected sample at the edge and in the interior so that sample identity is no longer tied to one position zone.'),
    'no_spatial_comparison': ('Obtain matched position measurements', 'Repeat the same sample or control material in both edge and interior wells. A pooled comparison across different sample identities cannot answer the position question.'),
    'replicates': ('Add repeated measurements', 'Identify samples represented by one well. Plan technical replication to assess measurement variability, and discuss independent biological replication separately.'),
    'partial': ('Confirm the unmeasured positions', 'Check that missing wells were intentionally omitted and were not lost during export. Unmeasured positions are not treated as zero.'),
}


def decision_summary(report, rows):
    codes = {f['code'] for f in report['findings']}
    ordered = ('controls','mixed_controls','control_overlap','zprime','confounding','no_spatial_comparison','replicates','partial')
    actions = []
    for code in ordered:
        if code not in codes:
            continue
        # Good separation remains a review item, not an urgent failure.
        severity = next(f['level'] for f in report['findings'] if f['code'] == code)
        title, detail = ACTIONS[code]
        actions.append({'finding_code':code,'priority':'review' if severity=='warning' else 'check','title':title,'detail':detail,'evidence':next(f['evidence'] for f in report['findings'] if f['code']==code)})
    if not report['samples']:
        state, message = 'controls_only', 'This file contains controls only. You can review control measurements, but sample follow-up design is unavailable until sample wells are supplied.'
    elif codes & {'controls','mixed_controls','control_overlap'}:
        state, message = 'control_review_needed', 'Review the control information before interpreting sample responses. Follow-up design requires identified negative and positive control materials; a layout does not resolve uncertain control definitions.'
    elif 'confounding' in codes:
        state, message = 'position_check_suggested', 'Some sample IDs occur in only one position zone. A balanced follow-up can help investigate the position explanation.'
    else:
        state, message = 'researcher_review', 'The basic descriptive checks are available. Review the evidence against assay-specific criteria; this is not an assay pass or biological validation.'
    canonical = json.dumps(sorted(rows,key=lambda r:r['well']),sort_keys=True,separators=(',',':'),allow_nan=False)
    return {'state':state,'message':message,'actions':actions,'decision_boundary':'The researcher decides which interpretation and follow-up are appropriate. The app does not convert a model preference or a QC metric into a biological conclusion.','analysis_version':ANALYSIS_VERSION,'report_id':hashlib.sha256((ANALYSIS_VERSION+'\n'+canonical).encode()).hexdigest()[:16]}
