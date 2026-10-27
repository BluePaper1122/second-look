"""Production transport exercises the same assay routes through the WSGI contract."""
import io
import json
import unittest
from unittest.mock import patch
from wsgiref.util import setup_testing_defaults
from wsgiref.validate import validator
from assay import example
from gateway import Application,validate_origin

class GatewayTests(unittest.TestCase):
    def request(self,app,path='/',method='GET',payload=None,headers=None,validate=True):
        body=json.dumps(payload).encode() if payload is not None else b''
        env={};setup_testing_defaults(env)
        path,_,query=path.partition('?')
        env.update({'REQUEST_METHOD':method,'PATH_INFO':path,'QUERY_STRING':query,'HTTP_HOST':'research.example',
                    'CONTENT_TYPE':'application/json','CONTENT_LENGTH':str(len(body)),
                    'wsgi.input':io.BytesIO(body),'wsgi.errors':io.StringIO()})
        env.update(headers or {})
        response={}
        def start(status,headers,exc_info=None):response.update(status=int(status[:3]),headers=dict(headers))
        iterator=(validator(app) if validate else app)(env,start)
        try:response['body']=b''.join(iterator)
        finally:
            if hasattr(iterator,'close'):iterator.close()
        return response
    def test_real_inspection_through_validated_wsgi(self):
        result=self.request(Application('https://research.example'),'/api/inspect','POST',{'csv':example()})
        self.assertEqual(result['status'],200)
        self.assertEqual(len(json.loads(result['body'])['rows']),96)
        self.assertEqual(int(result['headers']['Content-Length']),len(result['body']))
    def test_origin_and_host_checks_ignore_forwarding_spoofs(self):
        for headers in ({'HTTP_HOST':'evil.example','HTTP_X_FORWARDED_HOST':'research.example'}, {'HTTP_ORIGIN':'https://evil.example'}):
            result=self.request(Application('https://research.example'),'/api/inspect','POST',{'csv':example()},headers)
            self.assertEqual(result['status'],403)
    def test_rate_limit_preserves_read_access(self):
        app=Application('https://research.example',request_limit=1)
        self.assertEqual(self.request(app,'/api/inspect','POST',{'csv':example()})['status'],200)
        denied=self.request(app,'/api/inspect','POST',{'csv':example()})
        self.assertEqual(denied['status'],429)
        self.assertEqual(denied['headers']['Retry-After'],'60')
        self.assertEqual(self.request(app,'/api/status')['status'],200)
    def test_security_headers_on_page_and_error(self):
        app=Application('https://research.example')
        for path in ('/','/missing'):
            response=self.request(app,path)
            self.assertIn('Content-Security-Policy',response['headers'])
            self.assertEqual(response['headers']['Cache-Control'],'no-store')
            self.assertEqual(response['headers']['Referrer-Policy'],'no-referrer')
            self.assertIn('Strict-Transport-Security',response['headers'])
    def test_head_omits_body_and_method_rejection_is_explicit(self):
        app=Application('https://research.example')
        response=self.request(app,'/',method='HEAD',validate=False)
        self.assertEqual(response['status'],200)
        self.assertEqual(response['body'],b'')
        rejected=self.request(app,'/',method='DELETE')
        self.assertEqual(rejected['status'],405)
        self.assertIn('POST',rejected['headers']['Allow'])
    def test_internal_exception_does_not_expose_context(self):
        with patch('server.inspect',side_effect=RuntimeError('secret-test-only')):
            response=self.request(Application('https://research.example'),'/api/inspect','POST',{'csv':example()})
        self.assertEqual(response['status'],500)
        self.assertNotIn(b'secret-test-only',response['body'])
    def test_invalid_origin_is_rejected_before_serving(self):
        for origin in (None,'http://public.example','https://name:pass@research.example','https://research.example/','https://RESEARCH.example','https://research.example:443'):
            with self.subTest(origin=origin),self.assertRaises(ValueError):validate_origin(origin)
        self.assertEqual(validate_origin('http://127.0.0.1:8080'),'127.0.0.1:8080')
    def test_path_traversal_not_exposed(self):
        self.assertEqual(self.request(Application('https://research.example'),'/../../LICENSE')['status'],404)
