import json
import math
import unittest
from collections import defaultdict
from unittest.mock import patch
from assay import parse_csv, inspect, plan, edge, example, csv_export
from server import model_review

class AssayTests(unittest.TestCase):
    def test_example_reproducibility(self):
        self.assertEqual(example(seed=19), example(seed=19))
        self.assertNotEqual(example(seed=19), example(seed=20))
    def test_csv_rejects_duplicates_nonfinite_bad_wells(self):
        header = 'plate_id,well,sample_id,value,control\n'
        for rows in ('p,A01,s,nan,sample\n', 'p,A13,s,2,sample\n', 'p,A01,s,2,sample\np,a1,s,2,sample\n', 'p,A01,s,inf,sample\n', 'p,A01,s,2,unknown\n', 'p,A01,s,2,sample\nq,A02,s,2,sample\n'):
            with self.subTest(rows=rows), self.assertRaises(ValueError): parse_csv(header+rows)
    def test_mapping_and_normalization(self):
        rows = parse_csv('p,w,s,v,c\nx,a1,abc,4,sample\n',dict(zip(('plate_id','well','sample_id','value','control'),('p','w','s','v','c'))))
        self.assertEqual(rows[0]['well'], 'A01')
    def test_independent_zprime_calculation(self):
        rows = parse_csv('plate_id,well,sample_id,value,control\np,A01,n,0,negative\np,B02,n,2,negative\np,A02,p,10,positive\np,B03,p,12,positive\n')
        value = inspect(rows)['facts']['z_prime']['value']
        self.assertAlmostEqual(value, 1-6*math.sqrt(2)/10)
    def test_matched_difference_independent_arithmetic(self):
        rows = parse_csv('plate_id,well,sample_id,value,control\np,A01,a,10,sample\np,B02,a,4,sample\np,A02,b,25,sample\np,B03,b,15,sample\n')
        self.assertEqual(inspect(rows)['facts']['matched_edge_difference']['value'], 8)
    def test_no_pooled_claim_when_unidentifiable(self):
        rows=parse_csv('plate_id,well,sample_id,value,control\np,A01,a,10,sample\np,B02,b,4,sample\n')
        report=inspect(rows)
        self.assertNotIn('matched_edge_difference',report['facts'])
        self.assertIn('confounding',[f['code'] for f in report['findings']])
    def test_references_exist_for_all_examples(self):
        for kind in ('clean','artifact','biology','both','confounded','missing_controls','inconsistent'):
            report=inspect(parse_csv(example(kind)))
            for f in report['findings']:
                for ref in f['evidence']: self.assertIn(ref,report['facts'])
            json.dumps(report, allow_nan=False)
    def test_distinct_control_materials_not_pooled(self):
        rows=parse_csv('plate_id,well,sample_id,value,control\np,A01,n1,0,negative\np,B02,n2,20,negative\np,A02,p,40,positive\np,B03,p,42,positive\n')
        report=inspect(rows)
        self.assertNotIn('z_prime',report['facts'])
        self.assertIn('mixed_controls',[f['code'] for f in report['findings']])
    def test_control_contrast_excludes_candidate_signal(self):
        rows=parse_csv('plate_id,well,sample_id,value,control\np,A01,n,12,negative\np,B02,n,10,negative\np,A02,s,1000,sample\np,B03,s,0,sample\n')
        report=inspect(rows)
        self.assertEqual(report['facts']['negative_matched_edge_difference']['value'],2)
    def test_within_zone_sd_excludes_between_zone_shift(self):
        rows=parse_csv('plate_id,well,sample_id,value,control\np,A01,s,101,sample\np,A02,s,103,sample\np,B02,s,1,sample\np,B03,s,3,sample\n')
        report=inspect(rows)
        self.assertEqual(len(report['replicate_summaries']),2)
        for summary in report['replicate_summaries']:
            self.assertAlmostEqual(report['facts'][summary['evidence'][-1]]['value'],math.sqrt(2))
    def test_single_well_sd_not_zero(self):
        report=inspect(parse_csv('plate_id,well,sample_id,value,control\np,A01,s,3,sample\n'))
        self.assertEqual(len(report['replicate_summaries'][0]['evidence']),2)
    def test_plan_constraints_many_budgets(self):
        for n in range(1,17):
            for seed in (1,2,80):
                p=plan([f's{i}' for i in range(n)],96,seed)
                self.assertEqual(len(p['rows']), 4*n+8)
                self.assertEqual(len({r['well'] for r in p['rows']}),len(p['rows']))
                groups=defaultdict(list)
                for r in p['rows']: groups[(r['control'],r['sample_id'])].append(r)
                for rs in groups.values():
                    self.assertEqual(sum(edge(r['well']) for r in rs),2)
                    self.assertEqual(len(rs),4)
    def test_budget_rejection_and_collision(self):
        for budget in (8,11,12.5,True,100):
            with self.assertRaises(ValueError): plan(['a','b'],budget)
        with self.assertRaises(ValueError): plan(['a','a'],24)
        p=plan(['negative_control'],12)
        self.assertEqual(len({r['sample_id'] for r in p['rows']}),3)
    def test_formula_export(self):
        self.assertIn("'=SUM",csv_export([{'sample_id':'=SUM(A1:A2)'}]))
    def test_missing_model_explicit(self):
        with patch.dict('os.environ',{},clear=True):
            self.assertEqual(model_review(inspect(parse_csv(example())))['mode'],'unavailable')
    def test_model_evidence_gate(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def read(self): return json.dumps({'choices':[{'message':{'content':'{"priorities":["invented"]}'}}]}).encode()
        with patch.dict('os.environ',{'NEBIUS_API_KEY':'test','NEBIUS_MODEL':'nvidia/test'}), patch('urllib.request.urlopen',return_value=Response()):
            with self.assertRaises(ValueError): model_review(inspect(parse_csv(example())))

if __name__=='__main__': unittest.main()
