import json
import subprocess
import time


def _is_at_least_one_pod_ready(podsJson: str):
    pods = json.loads(podsJson)
    for pod in pods['items']:
        if "status" in pod and "phase" in pod["status"]:
            phase = pod["status"]["phase"]
            if phase in ["Running", "Succeeded", "Failed"]:
                print(f"Pod {pod['metadata']['name']}: {phase}")
                return True
    return False

def run_cronjob(kubeConfigFile: str, cronJob: str, jobName: str):
    cmdCreateJob = [
        "kubectl",
        "--kubeconfig",
        kubeConfigFile,
        "create",
        "job",
        "--from",
        f"cronjob/{cronJob}",
        jobName
    ]

    yield " ".join(cmdCreateJob) + "\n"
    proc = subprocess.Popen(cmdCreateJob, stdout=subprocess.PIPE, encoding='utf-8')
    for line in proc.stdout.readlines():
        yield line + "\n"
    if proc.wait(timeout=10) == 0:
        cmdGetStatus = [
            "kubectl",
            "--kubeconfig",
            kubeConfigFile,
            "get",
            "pods",
            "-l",
            f"job-name={jobName}",
            "-o",
            "json"
        ]
        jobStarted = False
        while True:
            yield " ".join(cmdGetStatus) + "\n"
            result = subprocess.run(cmdGetStatus, stdout=subprocess.PIPE, encoding='utf-8')
            if result.returncode == 0:
                podsJson = result.stdout
                if _is_at_least_one_pod_ready(podsJson):
                    jobStarted = True
                    break

                time.sleep(1)
            else:
                print(f'Failed to get job status:\n{result.stdout}')
                break

        if jobStarted:
            cmdJobLogsFollow = [
                'kubectl',
                "--kubeconfig",
                kubeConfigFile,
                'logs',
                '--follow',
                f'jobs/{jobName}'
            ]
            yield " ".join(cmdJobLogsFollow) + "\n"
            proc = subprocess.Popen(cmdJobLogsFollow, stdout=subprocess.PIPE, encoding='utf-8')
            for line in proc.stdout.readlines():
                yield line + "\n"

def run_and_print_cronjob(kubeConfigFile: str, cronJob: str, jobName: str):
    for line in run_cronjob(kubeConfigFile, cronJob, jobName):
        print(line)
