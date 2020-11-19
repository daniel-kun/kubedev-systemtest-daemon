FROM python:3.8-slim
RUN pip install pipenv
RUN apt-get update && apt-get install -y apt-transport-https curl gnupg
RUN curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | tee -a /etc/apt/sources.list.d/kubernetes.list
RUN apt-get update
RUN apt-get install -y kubectl

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

ENV FLASK_APP="src:create_app()"
CMD pipenv run flask run -h 0.0.0.0 -p 5000
