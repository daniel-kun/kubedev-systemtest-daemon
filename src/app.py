import json
import os
from uuid import uuid4

from flask import Flask, Response, request

from .run import run_cronjob

apiKey = os.environ['KUBEDEV_SYSTEMTEST_DAEMON_APIKEY']
cronJob = os.environ['KUBEDEV_SYSTEMTEST_DAEMON_CRONJOB']
kubeConfig = os.environ['KUBEDEV_SYSTEMTEST_DAEMON_KUBECONFIG']
kubeConfigFile = '/tmp/kube_config'

lastExecutedJob = None

def create_app():
    app = Flask(__name__)

    with open(kubeConfigFile, 'w') as f:
        f.write(kubeConfig)

    @app.route('/execute', methods=['POST'])
    def execute():
        headers = request.headers
        if not 'Api-Key' in headers or headers['Api-Key'] != apiKey:
            return "Invalid Api-Key", 401
        else:
            print(f'Running cronjob')
            jobName = f"temp-job-{str(uuid4())[0:8]}"
            lastExecutedJob = jobName
            return Response(run_cronjob(kubeConfigFile, cronJob, jobName), mimetype="text/plain")

    return app
