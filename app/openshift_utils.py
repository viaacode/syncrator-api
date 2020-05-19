import os

OC_URL = os.environ.get('OC_URL', 'https://do-prd-okp-m0.do.viaa.be:8443')
OC_PROJECT_NAME = os.environ.get('OC_PROJECT_NAME', 'shared-components')
OC_USER = os.environ.get('OC_USER', 'configure_user')
OC_PASSWORD = os.environ.get('OC_PASSWORD', 'configure_pass')


def run(cmd, path=None):
    if path:
        cmd = f'cd {path} && {cmd}'

    if os.environ.get('FLASK_ENV') == 'TESTING':
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
    res = run(f"oc project {project_name}")
    return res


def oc_logout():
    res = run("oc logout")
    return res


def oc_delete_job(pod_name):
    res = run(f"oc delete jobs {pod_name}")
    return res


def oc_create_job():
    # TODO:...
    pass


def oc_create_template():
    # TODO:...
    pass
