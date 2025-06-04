# Configuração Gunicorn para Produção
# Arquivo: gunicorn.conf.py

import os

# Configurações básicas
bind = f"0.0.0.0:{os.environ.get('PORT', 10000)}"
workers = int(os.environ.get('WEB_CONCURRENCY', 2))
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2

# Configurações de logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configurações de processo
preload_app = True
daemon = False
pidfile = None
tmp_upload_dir = None

# Configurações de segurança
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configurações de performance
worker_tmp_dir = "/dev/shm"
forwarded_allow_ips = "*"
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}

# Hooks
def on_starting(server):
    server.log.info("🚀 Iniciando Firebase BI API com Gunicorn")

def on_reload(server):
    server.log.info("🔄 Recarregando aplicação")

def worker_int(worker):
    worker.log.info("⚠️ Worker interrompido pelo usuário")

def pre_fork(server, worker):
    server.log.info(f"👷 Worker {worker.pid} iniciando")

def post_fork(server, worker):
    server.log.info(f"✅ Worker {worker.pid} pronto")

def worker_abort(worker):
    worker.log.info(f"❌ Worker {worker.pid} abortado")

