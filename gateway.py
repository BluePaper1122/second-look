"""WSGI application for a managed HTTPS deployment; no HTTP server inheritance."""
from collections import deque
from email.message import Message
from http import HTTPStatus
import json
import os
import sys
import threading
import time
from urllib.parse import urlsplit
import uuid

from errors import AppError, error_payload
from server import APIRoutes

SECURITY_HEADERS=[('X-Content-Type-Options','nosniff'),('Cache-Control','no-store'),
                  ('Referrer-Policy','no-referrer'),
                  ('Permissions-Policy','camera=(), microphone=(), geolocation=()'),
                  ('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'")]


class GatewayRequest(APIRoutes):
    """The route contract is only path, headers, input stream and response capture."""
    def __init__(self,environ):
        self.path=environ.get('PATH_INFO','/')
        if environ.get('QUERY_STRING'):self.path+='?'+environ['QUERY_STRING']
        self.headers=Message()
        for name,value in environ.items():
            if name.startswith('HTTP_') and isinstance(value,str):
                self.headers[name[5:].replace('_','-')]=value
        for env,header in (('CONTENT_TYPE','Content-Type'),('CONTENT_LENGTH','Content-Length')):
            if environ.get(env) is not None:self.headers[header]=environ[env]
        self.rfile=environ['wsgi.input']
        self.request_id=uuid.uuid4().hex[:12]
        self.response=None
    def send(self,value,status=200,mime='application/json'):
        body=json.dumps(value,allow_nan=False).encode() if mime=='application/json' else value.encode() if isinstance(value,str) else value
        self.response=(status,[('Content-Type',mime),('Content-Length',str(len(body))),('X-Request-ID',self.request_id)]+SECURITY_HEADERS,body)


def validate_origin(origin):
    if not isinstance(origin,str):raise ValueError('Set SECOND_LOOK_PUBLIC_ORIGIN to the exact HTTPS origin of the deployment.')
    parts=urlsplit(origin)
    if parts.username or parts.password or not parts.hostname or parts.path or parts.query or parts.fragment:
        raise ValueError('The public origin must contain only a scheme and hostname, with an optional port; no trailing slash or credentials.')
    if parts.scheme!='https' and not (parts.scheme=='http' and parts.hostname in ('localhost','127.0.0.1')):
        raise ValueError('Public deployments require an HTTPS origin. HTTP is allowed only for local verification.')
    try:port=parts.port
    except ValueError:raise ValueError('The public-origin port is invalid.') from None
    hostname='['+parts.hostname+']' if ':' in parts.hostname else parts.hostname
    default=443 if parts.scheme=='https' else 80
    canonical=parts.scheme+'://'+hostname+((':'+str(port)) if port and port!=default else '')
    if origin!=canonical:raise ValueError('Use the canonical public origin: '+canonical)
    return parts.netloc


class Application:
    def __init__(self,origin,request_limit=120):
        self.host=validate_origin(origin);self.origin=origin
        if type(request_limit) is not int or not 1<=request_limit<=10000:raise ValueError('Request limit must be an integer from 1 to 10000.')
        self.request_limit=request_limit
        self.requests=deque();self.lock=threading.Lock()
    def allow_request(self):
        # A single deployment-wide cap does not trust spoofable forwarding/IP
        # headers. Provider calls have their own lower limits.
        with self.lock:
            now=time.monotonic()
            while self.requests and now-self.requests[0]>60:self.requests.popleft()
            if len(self.requests)>=self.request_limit:return False
            self.requests.append(now)
            return True
    def __call__(self,environ,start_response):
        request=GatewayRequest(environ)
        method=environ.get('REQUEST_METHOD','GET')
        try:
            if request.headers.get('Host')!=self.host:
                raise AppError('unexpected_host','Open the application through its configured address.',403)
            if request.headers.get('Origin') not in (None,self.origin):
                raise AppError('cross_origin','This request came from a different website. Open the application directly.',403)
            if method not in ('GET','HEAD','POST'):
                raise AppError('method_not_allowed','This request method is not supported.',405)
            if method=='POST' and not self.allow_request():
                raise AppError('request_rate_limit','The application is receiving too many requests. Retry shortly; your browser input is unchanged.',429,True)
            if method=='POST':request.post()
            else:request.get()
        except AppError as e:
            request.send(error_payload(e,request.request_id),e.status)
        except (TimeoutError,ConnectionError,OSError):
            request.send(error_payload(AppError('request_interrupted','The request did not complete. Your browser input is unchanged; retry when connected.',408,True),request.request_id),408)
        except ValueError as e:
            request.send(error_payload(AppError('invalid_input',str(e)),request.request_id),400)
        except (TypeError,KeyError):
            request.send(error_payload(AppError('invalid_input','Some request fields are missing or unsupported.'),request.request_id),400)
        except Exception as e:
            print(json.dumps({'event':'request_failed','request_id':request.request_id,'type':type(e).__name__}),file=sys.stderr)
            request.send(error_payload(AppError('internal_error','The application could not complete this step. Your input is unchanged; retry or save it before restarting.',500,True),request.request_id),500)
        status,headers,body=request.response
        if status==405:headers.append(('Allow','GET, HEAD, POST'))
        if status==429:headers.append(('Retry-After','60'))
        if self.origin.startswith('https:'):headers.append(('Strict-Transport-Security','max-age=86400'))
        start_response(str(status)+' '+HTTPStatus(status).phrase,headers)
        return [] if method=='HEAD' else [body]


def create_app(origin=None):
    try:limit=int(os.getenv('SECOND_LOOK_REQUESTS_PER_MINUTE','120'))
    except ValueError:raise ValueError('SECOND_LOOK_REQUESTS_PER_MINUTE must be an integer.') from None
    return Application(origin or os.getenv('SECOND_LOOK_PUBLIC_ORIGIN'),request_limit=limit)
