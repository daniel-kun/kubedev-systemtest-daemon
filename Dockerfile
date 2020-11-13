FROM python:3.8-slim
RUN pip install pipenv

RUN groupadd --gid 3001 kubedev && \
        useradd --create-home --no-log-init --gid kubedev --uid 2001 system-test-daemon
RUN mkdir -p /app && chown -R system-test-daemon:kubedev /app
USER system-test-daemon

WORKDIR /app
COPY --chown=system-test-daemon:kubedev Pipfile Pipfile.lock ./
RUN pipenv install
COPY --chown=system-test-daemon:kubedev ./src/ ./src/

# generate bytecode ahead of time
RUN python3 -m compileall .

CMD pipenv run gunicorn "src:create_app()" -b 0.0.0.0:5000 --log-level debug
