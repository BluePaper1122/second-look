"""HTTP contract checks exercise real request parsing and recovery, not a mock API."""
import http.client
import json
import threading
import unittest
import urllib.error
from unittest.mock import patch
from assay import example, inspect, parse_csv
from errors import AppError
from server import Handler, LocalServer, model_review, MODEL_CALLS

class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=LocalServer(('127.0.0.1',0),Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)
    def request(self,path,body=None,headers=None,method='POST'):
        conn=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=3)
        h={'Content-Type':'application/json'}
        h.update(headers or {})
        conn.request(method,path,body,h)
        response=conn.getresponse()
        status=response.status
        payload=json.loads(response.read())
        conn.close()
        return status,payload
    def test_bad_json_then_successful_request(self):
        status,body=self.request('/api/inspect','{broken')
        self.assertEqual((status,body['code']),(400,'invalid_json'))
        self.assertIn('request_id',body)
        status,body=self.request('/api/inspect',json.dumps({'csv':example()}))
        self.assertEqual(status,200)
        self.assertEqual(body['workflow']['state'],'position_check_suggested')
    def test_oversized_request_rejected_before_read(self):
        status,body=self.request('/api/inspect','x',{'Content-Length':'1100001'})
        self.assertEqual((status,body['code']),(413,'request_too_large'))
    def test_wrong_content_type(self):
        status,body=self.request('/api/inspect','{}',{'Content-Type':'text/plain'})
        self.assertEqual((status,body['code']),(415,'unsupported_media'))
    def test_cross_origin_and_host_rejected(self):
        for h in ({'Origin':'https://unrelated.example'},{'Host':'unrelated.example'}):
            status,_=self.request('/api/inspect','{}',h)
            self.assertEqual(status,403)
    def test_invalid_budget_is_recoverable(self):
        data={'csv':example(),'samples':['candidate_edge','candidate_interior'],'budget':8,'controls':{'negative':'negative_control','positive':'positive_control'}}
        status,body=self.request('/api/plan',json.dumps(data))
        self.assertEqual(status,400)
        self.assertIn('16 wells',body['error'])
        data['budget']=24
        status,body=self.request('/api/plan',json.dumps(data))
        self.assertEqual(status,200)
        self.assertEqual(body['used'],16)
        self.assertIn('source_report_id',body)
    def test_no_key_is_explicit_and_local_analysis_survives(self):
        with patch.dict('os.environ',{},clear=True):
            status,body=self.request('/api/review',json.dumps({'csv':example()}))
            self.assertEqual((status,body['code']),(503,'model_unconfigured'))
            status,_=self.request('/api/inspect',json.dumps({'csv':example()}))
            self.assertEqual(status,200)
    def test_invalid_csv_has_recovery_message(self):
        status,body=self.request('/api/inspect',json.dumps({'csv':'plate_id,well,sample_id,value,control\np,A01,"broken'}))
        self.assertEqual((status,body['code']),(400,'invalid_csv'))
    def test_nonfinite_json_rejected(self):
        status,body=self.request('/api/inspect','{"csv":NaN}')
        self.assertEqual((status,body['code']),(400,'invalid_json'))
    def test_control_materials_required_and_preserved(self):
        data={'csv':example().replace('negative_control','vehicle').replace('positive_control','reference'),'samples':['candidate_edge'],'budget':12}
        status,body=self.request('/api/plan',json.dumps(data))
        self.assertEqual((status,body['code']),(400,'control_selection'))
        data['controls']={'negative':'vehicle','positive':'reference'}
        status,body=self.request('/api/plan',json.dumps(data))
        self.assertEqual(status,200)
        self.assertEqual({r['sample_id'] for r in body['rows'] if r['control']!='sample'},{'vehicle','reference'})
    def test_invalid_seed_does_not_silently_change_layout(self):
        data={'csv':example(),'samples':['candidate_edge'],'budget':12,'controls':{'negative':'negative_control','positive':'positive_control'},'seed':-1}
        status,body=self.request('/api/plan',json.dumps(data))
        self.assertEqual(status,400)
        self.assertIn('seed',body['error'])
    def test_saved_review_reopens_through_http_without_approval(self):
        source={'format':'second-look-review','version':1,'analysis_version':'0.2.0','input':{'csv':example()},'settings':{'samples':['candidate_edge'],'budget':12,'seed':11,'controls':{'negative':'negative_control','positive':'positive_control'}},'notes':'Synthetic workflow check','approved':True}
        status,body=self.request('/api/open-review',json.dumps({'session':source}))
        self.assertEqual(status,200)
        self.assertEqual(body['session']['notes'],'Synthetic workflow check')
        self.assertNotIn('approved',body)
        self.assertIn('report_id',body['workflow'])
    def test_invalid_review_file_returns_specific_error(self):
        status,body=self.request('/api/open-review',json.dumps({'session':{'version':999}}))
        self.assertEqual((status,body['code']),(400,'review_format'))
    def test_unknown_endpoint(self):
        status,body=self.request('/api/missing','{}')
        self.assertEqual((status,body['code']),(404,'not_found'))
    def test_internals_not_exposed_on_unexpected_failure(self):
        with patch('server.inspect',side_effect=RuntimeError('PRIVATE_INTERNAL_VALUE')):
            status,body=self.request('/api/inspect',json.dumps({'csv':example()}))
        self.assertEqual((status,body['code']),(500,'internal_error'))
        self.assertNotIn('PRIVATE_INTERNAL_VALUE',json.dumps(body))

class ProviderFailureTests(unittest.TestCase):
    def setUp(self): MODEL_CALLS.clear()
    def test_provider_failures_classified_without_body_leak(self):
        for http_code,code,status in ((401,'model_access',503),(402,'model_credit',503),(429,'provider_rate_limit',429),(500,'provider_unavailable',502)):
            with self.subTest(http_code=http_code), patch.dict('os.environ',{'NEBIUS_API_KEY':'private','NEBIUS_MODEL':'nvidia/test'}), patch('urllib.request.urlopen',side_effect=urllib.error.HTTPError('url',http_code,'private provider detail',{},None)):
                with self.assertRaises(AppError) as context: model_review(inspect(parse_csv(example())))
                self.assertEqual((context.exception.code,context.exception.status),(code,status))
                self.assertNotIn('private',str(context.exception))
    def test_timeout_is_retryable_but_never_a_success(self):
        with patch.dict('os.environ',{'NEBIUS_API_KEY':'private','NEBIUS_MODEL':'nvidia/test'}),patch('urllib.request.urlopen',side_effect=TimeoutError()):
            with self.assertRaises(AppError) as context: model_review(inspect(parse_csv(example())))
            self.assertEqual(context.exception.code,'model_timeout')
            self.assertTrue(context.exception.retryable)
