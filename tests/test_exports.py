"""Exports preserve scientific scope, source identity and an explicit review step."""
import csv
import io
import unittest
from assay import parse_csv,inspect,example
from exports import prepare_plan,reviewed_plan,handoff
from errors import AppError

class ExportTests(unittest.TestCase):
    def setUp(self):
        self.rows=parse_csv(example());self.report=inspect(self.rows)
        self.data={'samples':['candidate_edge','candidate_interior'],'controls':{'negative':'negative_control','positive':'positive_control'},'budget':24,'seed':11}
        self.layout=prepare_plan(self.rows,self.report,self.data)
    def reviewed(self):
        return {**self.data,'reviewed':True,'source_report_id':self.layout['source_report_id'],'layout_id':self.layout['layout_id']}
    def test_equivalent_sample_selections_have_same_layout_identity(self):
        reversed_data={**self.data,'samples':list(reversed(self.data['samples']))}
        self.assertEqual(prepare_plan(self.rows,self.report,reversed_data)['layout_id'],self.layout['layout_id'])
    def test_export_requires_review_attestation(self):
        for value in (None,False,'true',1):
            with self.subTest(value=value),self.assertRaises(AppError):reviewed_plan(self.rows,self.report,{**self.reviewed(),'reviewed':value})
    def test_changed_measurements_reject_previous_layout(self):
        self.rows[0]['value']+=1
        with self.assertRaises(AppError) as result:reviewed_plan(self.rows,inspect(self.rows),self.reviewed())
        self.assertEqual((result.exception.code,result.exception.status),('stale_layout',409))
    def test_changed_seed_or_budget_requires_new_review(self):
        for changes in ({'seed':12},{'budget':28}):
            with self.subTest(changes=changes),self.assertRaises(AppError):reviewed_plan(self.rows,self.report,{**self.reviewed(),**changes})
    def test_reviewed_csv_preserves_allocations_and_trace_metadata(self):
        result=reviewed_plan(self.rows,self.report,self.reviewed())
        exported=list(csv.DictReader(io.StringIO(result['csv'])))
        expected={r['well']:(r['sample_id'],r['control']) for r in self.layout['rows']}
        self.assertEqual({r['well']:(r['sample_id'],r['control']) for r in exported},expected)
        for row in exported:
            self.assertEqual(row['source_report_id'],self.layout['source_report_id'])
            self.assertEqual(row['layout_id'],self.layout['layout_id'])
            self.assertEqual(row['review_status'],'researcher_attested')
            self.assertEqual(row['randomization_seed'],'11')
            self.assertTrue(row['exported_at_utc'])
    def test_handoff_omits_unreviewed_well_assignments(self):
        result=handoff(self.rows,self.report,{**self.data,'layout_present':True,'notes':'Check handling with colleague.'})
        self.assertFalse(result['includes_reviewed_layout'])
        self.assertIn('UNREVIEWED FOLLOW-UP DRAFT',result['text'])
        self.assertNotIn('technical_replicate',result['text'])
        self.assertIn('  | Check handling with colleague.',result['text'])
    def test_handoff_can_include_a_reviewed_proposal(self):
        result=handoff(self.rows,self.report,{**self.reviewed(),'include_layout':True})
        self.assertTrue(result['includes_reviewed_layout'])
        self.assertIn('REVIEWED FOLLOW-UP PROPOSAL',result['text'])
        self.assertIn(self.layout['layout_id'],result['text'])
        self.assertIn('identity, expertise, and assay validity are not verified',result['text'])
    def test_client_attribution_and_notes_are_not_scientific_findings(self):
        result=handoff(self.rows,self.report,{'provenance':'source\nFAKE HEADING','notes':'A note\nOBSERVATIONS'})
        self.assertIn('source FAKE HEADING',result['text'])
        self.assertIn('  | OBSERVATIONS',result['text'])
        self.assertIn('not independently verified',result['text'])
