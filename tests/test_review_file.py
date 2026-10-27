import unittest
from assay import REQUIRED, example, parse_csv, inspect
from errors import AppError
from review_file import open_review
from workflow import ANALYSIS_VERSION, decision_summary

class ReviewFileTests(unittest.TestCase):
    def source(self):
        csv=example(); rows=parse_csv(csv)
        return {'format':'second-look-review','version':1,'analysis_version':ANALYSIS_VERSION,
                'report_id':decision_summary(inspect(rows),rows)['report_id'],
                'input':{'csv':csv,'mapping':{k:k for k in REQUIRED}},'notes':'Check sample handling with colleague.',
                'settings':{'samples':['candidate_edge'],'budget':12,'seed':23,'controls':{'negative':'negative_control','positive':'positive_control'}}}
    def test_restores_input_and_settings_but_recomputes_report(self):
        source=self.source(); source['report']={'invented':'conclusion'}; source['approved']=True
        result=open_review(source)
        self.assertEqual(result['session']['notes'],source['notes'])
        self.assertEqual(result['session']['settings'],source['settings'])
        self.assertNotIn('invented',result['report'])
        self.assertNotIn('approved',result)
        self.assertEqual(result['warnings'],[])
    def test_old_analysis_disclosed(self):
        source=self.source(); source['analysis_version']='old'
        self.assertTrue(open_review(source)['warnings'])
    def test_tampered_report_id_disclosed(self):
        source=self.source(); source['report_id']='not-the-input'
        self.assertTrue(open_review(source)['warnings'])
    def test_unknown_or_duplicate_samples_rejected(self):
        for ids in (['invented'],['candidate_edge','candidate_edge']):
            source=self.source(); source['settings']['samples']=ids
            with self.assertRaises(AppError):open_review(source)
    def test_future_schema_not_misread(self):
        source=self.source(); source['version']=2
        with self.assertRaises(AppError):open_review(source)
    def test_control_identity_not_silently_replaced(self):
        source=self.source(); source['settings']['controls']['negative']='not-present'
        with self.assertRaises(AppError):open_review(source)
    def test_notes_are_data_not_markup(self):
        source=self.source(); source['notes']='<script>not executable</script>'
        self.assertEqual(open_review(source)['session']['notes'],source['notes'])
    def test_invalid_budget_and_oversized_notes_rejected(self):
        source=self.source(); source['settings']['budget']=True
        with self.assertRaises(AppError):open_review(source)
        source=self.source(); source['notes']='x'*10001
        with self.assertRaises(AppError):open_review(source)
