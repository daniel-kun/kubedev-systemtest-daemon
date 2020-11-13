import os
import subprocess

from flask import Flask, Response, request

apiKey = os.environ['KUBEDEV_SYSTEMTEST_DAEMON_APIKEY']
dockerCommand = os.environ['KUBEDEV_SYSTEMTEST_DAEMON_DOCKER_COMMAND']

def generate_command_output(cmd: str):
    proc = subprocess.Popen(['/bin/sh', '-c', cmd], stdout=subprocess.PIPE)
    for line in proc.stdout.readlines():
        yield line


def create_app():
    app = Flask(__name__)

    @app.route('/execute', methods=['POST'])
    def execute():
        headers = request.headers
        if not 'Api-Key' in headers or headers['Api-Key'] != apiKey:
            return "Invalid Api-Key", 401
        else:
            print(f'Run docker command {dockerCommand}...')
            return Response(generate_command_output(dockerCommand), mimetype="text/plain")

    return app
