FROM apache/superset:4.1.1

USER root
COPY requirements-local.txt /tmp/requirements-local.txt
RUN pip install --no-cache-dir -r /tmp/requirements-local.txt
USER superset
