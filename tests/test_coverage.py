import unittest
from assay import parse_csv, inspect
from exports import prepare_plan, handoff

class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.rows=parse_csv('plate_id,well,sample_id,value,control\np,A01,a,1,sample\np,A02,a,2,sample\np,B02,b,3,sample\np,C02,b,4,sample\np,A03,n,0,negative\np,B03,p,10,positive\n')
        self.settings={'samples':['a','b'],'controls':{'negative':'n','positive':'p'},'budget':16,'seed':11}
    def test_coverage_reveals_the_specific_gap_and_proposed_crossing(self):
        coverage=prepare_plan(self.rows,inspect(self.rows),self.settings)['coverage']
        self.assertEqual(coverage['samples_gaining_coverage'],2)
        by_id={m['sample_id']:m for m in coverage['materials']}
        self.assertEqual(by_id['a']['observed'],{'edge':2,'interior':0})
        self.assertEqual(by_id['b']['observed'],{'edge':0,'interior':2})
        self.assertEqual(by_id['a']['observed_wells']['edge'],['A01','A02'])
        for material in coverage['materials']:
            self.assertEqual(material['proposed'],{'edge':2,'interior':2})
            self.assertTrue(material['proposed_crossed'])
    def test_already_crossed_material_does_not_claim_new_coverage(self):
        self.rows[1]['well']='D02'
        coverage=prepare_plan(self.rows,inspect(self.rows),{**self.settings,'samples':['a']})['coverage']
        self.assertEqual(coverage['samples_gaining_coverage'],0)
        self.assertIn('already occur',coverage['summary'])
        self.assertIn('no measured outcomes',coverage['limits'])
    def test_only_reviewed_handoff_includes_proposal_coverage(self):
        report=inspect(self.rows);layout=prepare_plan(self.rows,report,self.settings)
        unreviewed=handoff(self.rows,report,{**self.settings,'layout_present':True})['text']
        self.assertNotIn('OBSERVED VERSUS PROPOSED POSITION COVERAGE',unreviewed)
        reviewed=handoff(self.rows,report,{**self.settings,'include_layout':True,'reviewed':True,'layout_id':layout['layout_id'],'source_report_id':layout['source_report_id']})['text']
        self.assertIn('OBSERVED VERSUS PROPOSED POSITION COVERAGE',reviewed)
        self.assertIn('no measured outcomes',reviewed)
        self.assertIn('A01',reviewed)
