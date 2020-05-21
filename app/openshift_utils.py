import os
import subprocess

OC_URL = os.environ.get('OC_URL', 'https://do-prd-okp-m0.do.viaa.be:8443')
OC_PROJECT_NAME = os.environ.get('OC_PROJECT_NAME', 'shared-components')
OC_USER = os.environ.get('OC_USER', 'configure_user')
OC_PASSWORD = os.environ.get('OC_PASSWORD', 'configure_pass')
JOB_TEMPLATE_PARAMETER_PATH = "syncrator-openshift/job_params"


def oc_execute(cmd, path=None, dryrun=False):
    if path:
        cmd = f'cd {path} && {cmd}'

    if dryrun or os.environ.get('FLASK_ENV') == 'TESTING':
        return cmd
    else:
        output_stream = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE).stdout
        return output_stream.read().decode("utf-8")


def oc_login():
    login = 'oc login {} -p "{}" -u "{}" --insecure-skip-tls-verify > /dev/null'.format(
        OC_URL, OC_USER, OC_PASSWORD)
    commands = "{} ; {}".format(
        login,
        oc_project(OC_PROJECT_NAME)
    )

    return commands


def oc_logout():
    return "oc logout"


def oc_project(project_name):
    return f"oc project {project_name}"


def oc_delete_job(pod_name):
    return f"oc delete jobs {pod_name}"


def oc_create_job(
        template_params,
        template='syncrator-openshift/job_template.yaml'
):
    job_command = f"oc process -f {template} "

    for key, val in template_params.items():
        job_command += f'-p {key}="{val}" '

    job_command += "| oc create -f -"

    return job_command


def oc_create_syncrator_pod(job_params, dryrun=False):
    delete_previous_job = oc_delete_job(
        "syncrator-{}-{}-{}".format(
            job_params['ENV'],
            job_params['TARGET'],
            job_params['ACTION']
        )
    )

    # chaining commands to keep oc session available
    return oc_execute(
        '{} ; {} ; {}'.format(
            oc_login(),
            delete_previous_job,
            oc_create_job(job_params)
        ),
        dryrun=dryrun
    )


def oc_delete_syncrator_pod(env, target, job_type):
    delete_pod = oc_delete_job(
        "syncrator-{}-{}-{}".format(
            env,
            target,
            job_type
        )
    )

    # chaining commands to keep oc session available
    return oc_execute('{} ; {}'.format(
        oc_login(),
        delete_pod
    )
    )


def read_params_file(
        environment,
        target,
        job_type,
        params_path=JOB_TEMPLATE_PARAMETER_PATH):
    # ex: qas, avo, delta
    params_filename = f"{params_path}/{environment}/{target}-{job_type}.public_params"

    template_params = {}
    pf = open(params_filename)
    params = pf.read().split('\n')

    for p in params:
        if len(p) > 0:
            key, value = p.split('=')
            # template_params[key] = value # strip quotes in OPTIONS in
            # configfiles first
            template_params[key] = value.replace('"', '')
    pf.close()

    return template_params
