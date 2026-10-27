FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PORT=8080 SECOND_LOOK_BIND_HOST=0.0.0.0
WORKDIR /app
COPY requirements-production.txt .
RUN python -m pip install --no-cache-dir --require-hashes -r requirements-production.txt
COPY --chown=10001:10001 . .
USER 10001:10001
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "import os,urllib.request,urllib.parse; host=urllib.parse.urlsplit(os.environ['SECOND_LOOK_PUBLIC_ORIGIN']).netloc; request=urllib.request.Request('http://127.0.0.1:'+os.environ.get('PORT','8080')+'/api/status',headers={'Host':host}); assert urllib.request.urlopen(request,timeout=3).status==200"
CMD ["python", "serve.py"]
