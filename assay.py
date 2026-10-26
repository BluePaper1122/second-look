"""Deterministic exploratory QC. No causal inference or automatic correction."""
import csv
import io
import math
import random
import re
import statistics as st
from collections import defaultdict

REQUIRED = ('plate_id', 'well', 'sample_id', 'value', 'control')
CONTROLS = {'sample', 'negative', 'positive'}

def edge(well):
    return well[0] in 'AH' or int(well[1:]) in (1, 12)

def parse_csv(text, mapping=None):
    if not isinstance(text, str) or len(text.encode()) > 1_000_000:
        raise ValueError('Upload a CSV smaller than 1 MB.')
    reader = csv.DictReader(io.StringIO(text.lstrip('\ufeff')))
    mapping = mapping or {k: k for k in REQUIRED}
    if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
        raise ValueError('CSV headers must be present and unique.')
    if any(mapping.get(k) not in reader.fieldnames for k in REQUIRED):
        raise ValueError('Map all five required columns before inspecting.')
    if len(set(mapping[k] for k in REQUIRED)) != len(REQUIRED):
        raise ValueError('Each required field needs a different CSV column.')
    rows, seen = [], set()
    for line, raw in enumerate(reader, 2):
        if len(rows) >= 96:
            raise ValueError('This prototype supports one plate with at most 96 wells.')
        r = {k: (raw.get(mapping[k]) or '').strip() for k in REQUIRED}
        if any(not r[k] or len(r[k]) > 120 for k in ('plate_id', 'sample_id')):
            raise ValueError(f'Line {line}: plate and sample IDs are required (maximum 120 characters).')
        match = re.fullmatch(r'([A-Ha-h])0?([1-9]|1[0-2])', r['well'])
        if not match:
            raise ValueError(f'Line {line}: well must be A01–H12.')
        r['well'] = f'{match[1].upper()}{int(match[2]):02d}'
        r['control'] = r['control'].lower()
        if r['control'] not in CONTROLS:
            raise ValueError(f'Line {line}: control must be sample, negative, or positive.')
        try:
            r['value'] = float(r['value'])
        except ValueError:
            raise ValueError(f'Line {line}: measurement must be numeric.') from None
        if not math.isfinite(r['value']) or abs(r['value']) > 1e100:
            raise ValueError(f'Line {line}: measurement must be finite and within supported range.')
        key = (r['plate_id'], r['well'])
        if key in seen:
            raise ValueError(f'Line {line}: duplicate well {r["well"]}.')
        seen.add(key)
        rows.append(r)
    if not rows:
        raise ValueError('The CSV has no measurements.')
    if len({r['plate_id'] for r in rows}) != 1:
        raise ValueError('Inspect one plate at a time in this prototype.')
    by_sample = defaultdict(set)
    for r in rows:
        by_sample[r['sample_id']].add(r['control'])
    if any(len(v) > 1 for v in by_sample.values()):
        raise ValueError('A sample ID cannot mix sample and control roles.')
    return rows

def inspect(rows):
    facts, findings = {}, []
    def fact(key, value, units, wells):
        facts[key] = {'value': value, 'units': units, 'wells': wells}
    def finding(code, level, title, detail, ids):
        findings.append(dict(code=code, level=level, title=title, detail=detail, evidence=ids))
    fact('well_count', len(rows), 'wells', [r['well'] for r in rows])
    groups = {role: [r for r in rows if r['control'] == role] for role in CONTROLS}
    for role, group in sorted(groups.items()):
        fact(role + '_count', len(group), 'wells', [r['well'] for r in group])
    if len(rows) < 96:
        finding('partial', 'note', 'Partial plate', 'Unmeasured wells remain empty. They are never replaced with zero.', ['well_count'])
    if any(len(groups[x]) < 2 for x in ('positive', 'negative')):
        finding('controls', 'warning', 'Control information is limited', 'At least two positive and two negative controls are needed for this prototype’s Z-prime calculation. More controls and assay-specific review are needed for reliable QC.', ['positive_count', 'negative_count'])
    else:
        p, n = ([r['value'] for r in groups[x]] for x in ('positive', 'negative'))
        sep = abs(st.mean(p) - st.mean(n))
        if sep:
            z = 1 - 3 * (st.stdev(p) + st.stdev(n)) / sep
            fact('z_prime', z, 'dimensionless', [r['well'] for r in groups['positive'] + groups['negative']])
            finding('zprime', 'warning' if z < .5 else 'note', 'Control separation', 'Z-prime summarizes control separation and variability. The exploratory reference of 0.5 is not a universal assay acceptance rule.', ['z_prime'])
        else:
            finding('control_overlap', 'warning', 'Controls have identical means', 'Z-prime is undefined because the control means coincide.', ['positive_count', 'negative_count'])
    samples = defaultdict(list)
    for r in groups['sample']:
        samples[r['sample_id']].append(r)
    confounded, crossed = [], []
    for sid, rs in sorted(samples.items()):
        zones = {edge(r['well']) for r in rs}
        (crossed if len(zones) == 2 else confounded).append(sid)
    fact('uncrossed_sample_count', len(confounded), 'sample IDs', [r['well'] for r in groups['sample'] if r['sample_id'] in confounded])
    if confounded:
        finding('confounding', 'warning', 'Sample identity and position may be entangled', 'Some sample IDs occur only at the edge or only in the interior. Their measured response cannot by itself distinguish sample effects from position effects. This is a design limitation, not proof of an artifact.', ['uncrossed_sample_count'])
    # Matched within-ID contrasts, never a pooled edge-vs-interior causal claim.
    differences = []
    matched_wells = []
    all_groups = defaultdict(list)
    for r in rows:
        all_groups[(r['control'], r['sample_id'])].append(r)
    for rs in all_groups.values():
        e, i = ([r['value'] for r in rs if edge(r['well']) == flag] for flag in (True, False))
        if e and i:
            differences.append(st.mean(e) - st.mean(i))
            matched_wells.extend(r['well'] for r in rs)
    if differences:
        fact('matched_edge_difference', st.mean(differences), 'measurement units; equal weight per sample ID', matched_wells)
        fact('matched_id_count', len(differences), 'sample IDs', matched_wells)
        finding('spatial', 'note', 'Matched position comparison available', 'This is the mean within-sample edge-minus-interior difference, including controls. It is descriptive, unadjusted for row, batch, or other factors, and does not establish a cause.', ['matched_edge_difference', 'matched_id_count'])
    else:
        finding('no_spatial_comparison', 'warning', 'No matched position comparison', 'No sample or control ID spans both edge and interior positions. A pooled comparison would mix position with sample identity, so it is withheld.', ['uncrossed_sample_count'])
    singles = [sid for sid, rs in samples.items() if len(rs) < 2]
    fact('unreplicated_sample_count', len(singles), 'sample IDs', [r['well'] for r in groups['sample'] if r['sample_id'] in singles])
    if singles:
        finding('replicates', 'warning', 'Some samples lack within-plate replication', 'One measurement cannot estimate within-sample variability. Repeated wells are technical replicates unless independent biological replication is documented.', ['unreplicated_sample_count'])
    return {'facts': facts, 'findings': findings, 'samples': sorted(samples), 'scope': 'Exploratory single-plate QC. No automatic correction, significance tests, hit ranking, or biological validation.'}

def plan(sample_ids, budget, seed=11):
    if isinstance(budget, bool) or not isinstance(budget, int) or not 8 <= budget <= 96:
        raise ValueError('Choose an integer well budget from 8 to 96.')
    if not isinstance(sample_ids, list) or not sample_ids or len(sample_ids) != len(set(sample_ids)):
        raise ValueError('Select at least one unique sample ID.')
    if any(not isinstance(s, str) or not s or len(s) > 120 for s in sample_ids):
        raise ValueError('Invalid sample ID.')
    # Two wells per zone for each sample, and two per zone for each control.
    needed = 4 * len(sample_ids) + 8
    if needed > budget:
        raise ValueError(f'This design needs {needed} wells. Increase the budget or select fewer samples.')
    if needed // 2 > 36:
        raise ValueError('The 96-well plate has only 36 edge positions. Select at most 16 samples.')
    rng = random.Random(seed)
    wells = [f'{r}{c:02d}' for r in 'ABCDEFGH' for c in range(1, 13)]
    zones = {flag: [w for w in wells if edge(w) == flag] for flag in (True, False)}
    for pool in zones.values():
        rng.shuffle(pool)
    result = []
    control_ids = []
    for role in ('negative', 'positive'):
        sid = role + '_control'
        while sid in sample_ids:
            sid = '_' + sid
        control_ids.append((sid, role))
    allocations = control_ids + [(s, 'sample') for s in sample_ids]
    for sid, role in allocations:
        for flag in (True, False):
            for rep in range(1, 3):
                result.append({'plate_id': 'followup', 'well': zones[flag].pop(), 'sample_id': sid, 'control': role, 'zone': 'edge' if flag else 'interior', 'technical_replicate': rep})
    result.sort(key=lambda r: r['well'])
    return {'rows': result, 'used': needed, 'budget': budget, 'unused': budget-needed, 'seed': seed, 'explanation': 'Each selected sample and each control has two technical replicates at the edge and two in the interior. Randomization is stratified by position. This tests an edge/interior explanation; it does not balance every row, column, or biological factor. Confirm assay compatibility before use.'}

def example(kind='confounded', seed=11):
    if kind not in ('confounded', 'clean', 'artifact', 'biology', 'both', 'missing_controls', 'inconsistent'):
        raise ValueError('Unknown example.')
    rng = random.Random(seed)
    wells = [f'{r}{c:02d}' for r in 'ABCDEFGH' for c in range(1, 13)]
    rng.shuffle(wells)
    rows = []
    for index, well in enumerate(wells):
        role = 'negative' if index < 12 else 'positive' if index < 24 else 'sample'
        if kind == 'missing_controls':
            role = 'sample'
        sid = role + '_control' if role != 'sample' else ('candidate_edge' if edge(well) else 'candidate_interior') if kind == 'confounded' else f'candidate_{index % 6 + 1}'
        value = 180 if role == 'positive' else 100
        if role == 'sample' and sid == 'candidate_1' and kind in ('biology', 'both'):
            value += 45
        if edge(well) and kind in ('confounded', 'artifact', 'both'):
            value += 35
        value += rng.gauss(0, 30 if kind == 'inconsistent' else 3)
        rows.append(dict(plate_id='synthetic_demo', well=well, sample_id=sid, value=round(value, 3), control=role))
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=REQUIRED)
    writer.writeheader()
    writer.writerows(sorted(rows, key=lambda r: r['well']))
    return out.getvalue()

def csv_export(rows):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=list(rows[0]))
    writer.writeheader()
    for row in rows:
        # Prevent spreadsheet formula execution from untrusted identifiers.
        writer.writerow({k: "'" + v if isinstance(v, str) and v.startswith(('=', '+', '-', '@', '\t', '\r')) else v for k, v in row.items()})
    return out.getvalue()
