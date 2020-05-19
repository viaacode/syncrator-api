import os

OC_URL = os.environ.get('OC_URL', 'https://do-prd-okp-m0.do.viaa.be:8443')
OC_PROJECT_NAME = os.environ.get('OC_PROJECT_NAME', 'shared-components')
OC_USER = os.environ.get('OC_USER', 'configure_user')
OC_PASSWORD = os.environ.get('OC_PASSWORD', 'configure_pass')


def run(cmd, path=None, dryrun=False):
    if path:
        cmd = f'cd {path} && {cmd}'

    if dryrun or os.environ.get('FLASK_ENV') == 'TESTING':
        print(f"DRYRUN cmd: {cmd}")
        return cmd
    else:
        output_stream = os.popen(cmd)
        return output_stream.read()


def oc_login():
    res = run(
        f"oc login {OC_URL} -p '{OC_USER}' -u '{OC_PASSWORD}' --insecure-skip-tls-verify > /dev/null")

    # for ease of use also switch to configured project
    oc_project(OC_PROJECT_NAME)
    return res


def oc_project(project_name):
    return run(f"oc project {project_name}")


def oc_logout():
    return run("oc logout")


def oc_delete_job(pod_name):
    return run(f"oc delete jobs {pod_name}")


def oc_create_job(
        template_params,
        template='syncrator-openshift/job_template.yaml',
        dryrun=False
):
    job_command = f"oc process -f {template} "

    for key, val in template_params.items():
        job_command += f'-p {key}="{val}" '

    job_command += "| oc create -f -"
    print("create job cmd: {}".format(job_command))

    return run(job_command, dryrun)


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
