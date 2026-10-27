"""Scripted model outputs test orchestration, not actual model performance."""
import copy
import math
import unittest
from analysis_tools import execute_tool
from agent_review import run_review
from assay import example, parse_csv, inspect
from errors import AppError

class ToolTests(unittest.TestCase):
    def test_scoped_control_pair_excludes_other_materials(self):
        rows=parse_csv('plate_id,well,sample_id,value,control\np,A01,n,0,negative\np,B02,n,2,negative\np,A02,p,10,positive\np,B03,p,12,positive\np,A03,other,1000,negative\n')
        result=execute_tool({'name':'control_pair','arguments':{}},rows,{'controls':{'negative':'n','positive':'p'}})
        self.assertAlmostEqual(result['z_prime'],1-6*math.sqrt(2)/10)
        self.assertEqual(result['values']['negative']['sample_id'],'n')
    def test_single_zone_does_not_fabricate_contrast(self):
        rows=parse_csv(example())
        result=execute_tool({'name':'sample_position','arguments':{'sample_id':'candidate_edge'}},rows,{'samples':['candidate_edge']})
        self.assertEqual(result['status'],'needs_data')
        self.assertIsNone(result['edge_minus_interior'])
    def test_unselected_sample_rejected(self):
        with self.assertRaises(AppError):
            execute_tool({'name':'sample_position','arguments':{'sample_id':'candidate_edge'}},parse_csv(example()),{'samples':[]})
    def test_feasibility_leaves_settings_and_measurements_unchanged(self):
        rows=parse_csv(example());settings={'samples':['candidate_edge'],'controls':{'negative':'negative_control','positive':'positive_control'},'budget':8}
        before=copy.deepcopy((rows,settings))
        result=execute_tool({'name':'design_feasibility','arguments':{}},rows,settings)
        self.assertEqual(result['values']['required_wells'],12)
        self.assertEqual(result['status'],'needs_settings')
        self.assertEqual((rows,settings),before)
    def test_tool_cannot_replace_controls_or_run_arbitrary_code(self):
        for call in ({'name':'control_pair','arguments':{'negative':'different'}},{'name':'execute_python','arguments':{}}):
            with self.assertRaises(AppError):execute_tool(call,parse_csv(example()),{})

class AgentReviewTests(unittest.TestCase):
    def setUp(self):
        self.rows=parse_csv(example());self.report=inspect(self.rows)
        self.settings={'samples':['candidate_edge'],'controls':{'negative':'negative_control','positive':'positive_control'},'budget':12}
        self.plan={'tool_calls':[{'name':'sample_position','arguments':{'sample_id':'candidate_edge'}}]}
        self.result={'priorities':['confounding'],'evidence_ids':['analysis_1'],'next_action':'confounding'}
    def run_script(self,plan=None,result=None,objective='position'):
        outputs=iter([self.plan if plan is None else plan,self.result if result is None else result]);requests=[]
        def fake(prompt):
            requests.append(prompt)
            return {'mode':'live','model':'nvidia/scripted-test-only','payload':next(outputs)}
        return run_review(self.rows,self.report,objective,self.settings,fake),requests
    def test_two_stages_include_actual_computed_evidence(self):
        result,requests=self.run_script()
        self.assertEqual(len(requests),2)
        self.assertEqual(requests[1]['computed_analyses'][0]['status'],'needs_data')
        self.assertEqual(result['runtime_calls'],2)
        self.assertIn('source_report_id',result)
        self.assertEqual(result['next_action']['finding_code'],'confounding')
    def test_unknown_evidence_rejected(self):
        invalid={**self.result,'evidence_ids':['not-computed']}
        with self.assertRaises(AppError):self.run_script(result=invalid)
    def test_unknown_action_rejected(self):
        with self.assertRaises(AppError):self.run_script(result={**self.result,'next_action':'approve_assay'})
    def test_duplicate_tool_calls_rejected(self):
        with self.assertRaises(AppError):self.run_script(plan={'tool_calls':self.plan['tool_calls']*2})
    def test_unrelated_analysis_does_not_satisfy_objective(self):
        with self.assertRaises(AppError):self.run_script(plan={'tool_calls':[{'name':'design_feasibility','arguments':{}}]})
    def test_missing_selection_never_spends_provider_call(self):
        def forbidden(prompt):raise AssertionError('Provider must not be called')
        with self.assertRaises(AppError):run_review(self.rows,self.report,'position',{'samples':[]},forbidden)
    def test_unconfigured_model_remains_unavailable(self):
        result=run_review(self.rows,self.report,'position',self.settings,lambda _: {'mode':'unavailable','message':'Not configured'})
        self.assertEqual(result['mode'],'unavailable')
    def test_partial_completion_not_presented_as_success(self):
        outputs=iter([{'mode':'live','model':'test','payload':self.plan},{'mode':'unavailable'}])
        with self.assertRaises(AppError):run_review(self.rows,self.report,'position',self.settings,lambda _:next(outputs))
