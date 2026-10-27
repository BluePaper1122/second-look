"""Portable research sessions: restore inputs, recompute conclusions, reset approval."""
from assay import REQUIRED, parse_csv, inspect
from errors import AppError
from workflow import ANALYSIS_VERSION, decision_summary

FORMAT = 'second-look-review'
VERSION = 1


def open_review(value):
    if not isinstance(value, dict) or value.get('format') != FORMAT or type(value.get('version')) is not int or value['version'] != VERSION:
        raise AppError('review_format', 'Choose a Second Look review file with a supported format version. Your current work has not been replaced.')
    source = value.get('input')
    if not isinstance(source, dict):
        raise AppError('review_input', 'The review file is missing its original measurements. Your current work has not been replaced.')
    rows = parse_csv(source.get('csv'), source.get('mapping'))
    report = inspect(rows)
    flow = decision_summary(report, rows)
    notes = value.get('notes', '')
    if not isinstance(notes, str) or len(notes) > 10_000:
        raise AppError('review_notes', 'Review notes must be plain text with at most 10,000 characters.')
    settings = value.get('settings', {})
    if not isinstance(settings, dict):
        raise AppError('review_settings', 'The saved follow-up settings are unreadable. Your current work has not been replaced.')
    samples = settings.get('samples', [])
    if not isinstance(samples, list) or any(not isinstance(s, str) or s not in report['samples'] for s in samples) or len(set(samples)) != len(samples):
        raise AppError('review_samples', 'The saved selection contains unknown or repeated sample IDs. Your current work has not been replaced.')
    budget, seed = settings.get('budget', 24), settings.get('seed', 11)
    if type(budget) is not int or not 8 <= budget <= 96 or type(seed) is not int or not 0 <= seed <= 4294967295:
        raise AppError('review_settings', 'The saved budget or randomization seed is outside the supported range.')
    controls = settings.get('controls', {})
    if not isinstance(controls, dict) or any(not isinstance(controls.get(role, ''), str) or (controls.get(role) and controls[role] not in report['control_ids'][role]) for role in ('negative', 'positive')):
        raise AppError('review_controls', 'The saved controls do not match the original measurements.')
    mapping = source.get('mapping') or {k: k for k in REQUIRED}
    warnings = []
    if value.get('analysis_version') != ANALYSIS_VERSION:
        warnings.append('The analysis version has changed; all results were recalculated.')
    if value.get('report_id') and value['report_id'] != flow['report_id']:
        warnings.append('The saved report identifier differs from the recalculated report. Check whether the measurements or analysis version changed.')
    return {
        'rows': rows, 'report': report, 'workflow': flow,
        'session': {'input': {'csv': source['csv'], 'mapping': mapping}, 'notes': notes,
                    'settings': {'samples': samples, 'budget': budget, 'seed': seed,
                                 'controls': {role: controls.get(role, '') for role in ('negative','positive')}}},
        'warnings': warnings,
        'message': 'Review file opened. Measurements were reanalyzed; previous model responses and layout approval were not restored.'
    }
