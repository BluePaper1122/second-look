import unittest
from assay import example, parse_csv, inspect
from workflow import decision_summary

class WorkflowTests(unittest.TestCase):
    def test_report_id_stable_across_csv_row_order(self):
        rows=parse_csv(example())
        self.assertEqual(decision_summary(inspect(rows),rows)['report_id'],decision_summary(inspect(rows[::-1]),rows[::-1])['report_id'])
    def test_report_id_changes_with_measurements(self):
        rows=parse_csv(example()); original=decision_summary(inspect(rows),rows)['report_id']
        rows[0]['value']+=1
        self.assertNotEqual(original,decision_summary(inspect(rows),rows)['report_id'])
    def test_actions_reference_existing_findings_and_evidence(self):
        rows=parse_csv(example('missing_controls')); report=inspect(rows); summary=decision_summary(report,rows)
        self.assertEqual(summary['state'],'control_review_needed')
        for action in summary['actions']:
            self.assertIn(action['finding_code'],[f['code'] for f in report['findings']])
            for ref in action['evidence']: self.assertIn(ref,report['facts'])
    def test_controls_only_is_not_presented_as_sample_ready(self):
        rows=[r for r in parse_csv(example()) if r['control']!='sample']
        self.assertEqual(decision_summary(inspect(rows),rows)['state'],'controls_only')
