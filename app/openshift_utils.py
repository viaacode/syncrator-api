import os
import subprocess

OC_URL = os.environ.get('OC_URL', 'https://do-prd-okp-m0.do.viaa.be:8443')
OC_PROJECT_NAME = os.environ.get('OC_PROJECT_NAME', 'shared-components')
OC_USER = os.environ.get('OC_USER', 'configure_user')
OC_PASSWORD = os.environ.get('OC_PASSWORD', 'configure_pass')


def oc_run(cmd):
    return cmd


def oc_execute(cmd, path=None, dryrun=False):
    if path:
        cmd = f'cd {path} && {cmd}'

    if dryrun or os.environ.get('FLASK_ENV') == 'TESTING':
        print(f"DRYRUN cmd: {cmd}")
        return cmd
    else:
        output_stream = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE).stdout
        return output_stream.read().decode("utf-8")


def oc_login():
    res = oc_run(
        f'oc login {OC_URL} -p "{OC_USER}" -u "{OC_PASSWORD}" --insecure-skip-tls-verify > /dev/null')

    # for ease of use also switch to configured project
    res += " ; " + oc_project(OC_PROJECT_NAME)
    return res


def oc_logout():
    return oc_run("oc logout")


def oc_project(project_name):
    return oc_run(f"oc project {project_name}")


def oc_delete_job(pod_name):
    return oc_run(f"oc delete jobs {pod_name}")


def oc_create_job(
        template_params,
        template='syncrator-openshift/job_template.yaml'
):
    job_command = f"oc process -f {template} "

    for key, val in template_params.items():
        job_command += f'-p {key}="{val}" '

    job_command += "| oc create -f -"

    return oc_run(job_command)


def oc_create_syncrator_pod(job_params, dryrun=False):
    # chaining commands to keep oc session available
    cmd = oc_login()
    cmd += " ; " + oc_delete_job(
        "syncrator-{}-{}-{}".format(
            job_params['ENV'],
            job_params['TARGET'],
            job_params['ACTION']
        )
    )
    # gotcha the delete might fail if not are found!
    cmd += " ; " + oc_create_job(job_params)
    return oc_execute(cmd, dryrun=dryrun)


def oc_delete_syncrator_pod(env, target, job_type):
    # chaining commands to keep oc session available
    cmd = oc_login()
    cmd += " ; " + oc_delete_job(
        "syncrator-{}-{}-{}".format(
            env,
            target,
            job_type
        )
    )
    return oc_execute(cmd)


def read_params_file(
        environment,
        target,
        job_type,
        params_path="syncrator-openshift/job_params"):
    # ex: qas, avo, delta
    params_filename = f"{params_path}/{environment}/{target}-{job_type}.public_params"

    template_params = {}
    pf = open(params_filename)
    params = pf.read().split('\n')

    for p in params:
        if len(p) > 0:
            key, value = p.split('=')
            # template_params[key] = value # in future this is ok
            # we need to strip some extra quotes added last week in OPTIONS
            # that was mostly for getting the shell scripts working nicely
            template_params[key] = value.replace('"', '')
    pf.close()

    return template_params
