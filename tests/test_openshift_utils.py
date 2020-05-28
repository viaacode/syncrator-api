# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  tests/test_openshift_utils.py
#
from app.openshift_utils import (
    oc_create_job,
    read_params_file,
    oc_execute
)


def test_param_parsing():
    template_params = read_params_file(
        'qas', 'avo', 'delta',
        path='syncrator-openshift/job_params'
    )

    assert template_params == {
        'ACTION': 'delta',
        'ACTION_NAME': 'delta',
        'ENV': 'qas',
        'IS_TAG': 'latest',
        'OPTIONS': '-n 1000 -c 1',
        'TARGET': 'avo'
    }

    # test these params in oc_create command

    result = oc_create_job(template_params)
    assert result == ' '.join((
        'oc process -f syncrator-openshift/job_template.yaml',
        '-p ENV="qas" -p TARGET="avo"',
        '-p ACTION_NAME="delta" -p ACTION="delta"',
        '-p IS_TAG="latest"',
        '-p OPTIONS="-n 1000 -c 1" | oc create -f -'
    ))


def test_path_in_execute():
    path_command = oc_execute('ls *.py -1 | wc -l', path='tests')
    assert path_command == 'cd tests && ls *.py -1 | wc -l'
