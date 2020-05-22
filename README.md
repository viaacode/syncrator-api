# syncrator-api

## Synopsis

## Prerequisites

* Git
* Docker
* Python 3.6+
* Linux (if you want to run it locally, uwsgi is not available on other platforms.)
* Access to the meemoo PyPi

## Usage

1. Clone this repository with:

    `$ git clone https://github.com/viaacode/syncrator-api.git`

2. Change into the new directory.

### Running locally

1. Start by creating a virtual environment:

    `$ python -m venv ./venv`

2. Activate the virtual environment:

    `$ source ./venv/bin/activate`

3. Install the external modules:

    ```shell
    $ pip install -r requirements.txt \
        --extra-index-url http://do-prd-mvn-01.do.viaa.be:8081/repository/pypi-all/simple \
        --trusted-host do-prd-mvn-01.do.viaa.be && \
      pip install -r requirements-test.txt
    ```

4. Run the tests with:

    `$ python -m pytest -v`

5. Run the application:

   `$ uwsgi -i uwsgi.ini`

The application is now serving requests on `localhost:8080`. Try it with:

    `$ curl -v -X GET http://127.0.0.1:8080/`


### Running using Docker

1. Build the container:

   `$ docker build . -t syncrator-api`

2. Run the container:

   `$ docker run -p 8080:8080 syncrator-api`

You can try the same cURL commands as specified above.

### Helper scripts
To quickly install everything in a virtual env just run
``` scripts/install ```

To run the tests locally:
``` 
scripts/test
========================== test session starts ==========================
platform darwin -- Python 3.7.6, pytest-5.4.1, py-1.8.1, pluggy-0.13.1 -- /Users/wschrep/FreelanceWork/VIAA/syncrator-api/python_env/bin/python
cachedir: .pytest_cache
rootdir: /Users/wschrep/FreelanceWork/VIAA/syncrator-api
plugins: cov-2.8.1
collected 9 items

tests/test_app.py::test_home PASSED                               [ 11%]
tests/test_app.py::test_liveness_check PASSED                     [ 22%]
tests/test_app.py::test_dryrun_sync_job PASSED                    [ 33%]
tests/test_app.py::test_dryrun_delta_job PASSED                   [ 44%]
tests/test_app.py::test_dryrun_delete_job PASSED                  [ 55%]
tests/test_app.py::test_dryrun_generic_run PASSED                 [ 66%]
tests/test_app.py::test_list_jobs PASSED                          [ 77%]
tests/test_app.py::test_get_unknown_job PASSED                    [ 88%]
tests/test_app.py::test_get_existing_job PASSED                   [100%]

=========================== 9 passed in 0.79s ===========================
```

To run a server on port 8080:

``` 
scripts/run 
```
The root page has links and some minimal description of other available routes for api calls, open in your browser by
following this link <a href="http://127.0.0.1:8080/">Syncrator API</a> after you have the server running.



To build the docker containers:

```
scripts/build
```

During development you can autoformat using scripts/autopep and to make changes and see response instantly without restarting the application
theres the scripts/debug helper script now
```
scripts/debug
```
It also runs on port 8080 like the scripts/run and docker builds


### API calls available
```
GET /jobs - paginated list of active jobs
GET /jobs/<id> - get job details and progress

GET /sync/avo/qas - full synchronisation job dryrun
POST /sync/<project>/<env> - start a new full synchronisation job

GET /delta/avo/qas - delta synchronisation job dryrun
POST /delta/<project>/<env> - start a new delta synchronisation job

GET /delete/avo/qas - delete synchronisation job dryrun
POST /delete/<project>/<env> - start a new delete synchronisation job

GET /diff/avo/qas - dryrun for delta followed by delete in one go for partial updates
POST /diff/<project>/<env> - start delta job followed by a delete job

POST /run - start custom syncrator job by passing all template parameters (target, env, action_name, action, is_tag, options)
POST /dryrun - dryrun custom job by passing all template parameters (target, env, action_name, action, is_tag, options)
```


As mentioned in examples the sync, delta, delete (and to be implemented diff) calls can all be done
using the /run and /dryrun post's but you will need to exactly specify the 6 parameters that fill in the template.

### Paremetrised jobs
When using the simplified calls ex /sync/avo/qas or /delta/avo/prd these do a lookup in the parameter files defined 
in the directory 'syncrator-openshift/job_params'.
Here is a list of all currently defined params: 
```
syncrator-openshift/job_params
├── prd
│   ├── avo-delete.public_params
│   ├── avo-delta.public_params
│   ├── avo-sync.public_params
│   ├── cataloguspro-delete.public_params
│   ├── cataloguspro-delta.public_params
│   ├── cataloguspro-sync.public_params
│   ├── metadatacatalogus-delete.public_params
│   ├── metadatacatalogus-delta.public_params
│   └── metadatacatalogus-sync.public_params
└── qas
    ├── avo-delete.public_params
    ├── avo-delta.public_params
    ├── avo-sync.public_params
    ├── cataloguspro-delete.public_params
    ├── cataloguspro-delta.public_params
    ├── cataloguspro-sync.public_params
    ├── metadatacatalogus-delete.public_params
    ├── metadatacatalogus-delta.public_params
    └── metadatacatalogus-sync.public_params
```



### Examples

Example run a full sync on avo project in qas environment as dryrun we first want to see the template output. We use jq to show only the template result:
```
curl http://127.0.0.1:8080/sync/avo/qas | jq .result -r
```

To now have an actual syncrator pod startup just make same request but then with a post call:
```
curl -X POST http://127.0.0.1:8080/sync/avo/qas | jq .result -r
```


If you don't want or don't have a predifined template (.public_params file) you can start a custom syncrator job like so:

```
curl -X POST http://localhost:8080/dryrun -H 'Content-Type:application/json' \
  -d '{
    "target":"avo", 
    "env":"qas",
    "action_name": "delta",
    "action": "delta",
    "is_tag": "latest",
    "options": "-n 1000 -c 1"
    }'
```

This has the same result as doing following request as this already exists:
```
curl http://127.0.0.1:8080/delta/avo/qas
```

To make the actual pod start and execute the openshift commands use the path 'run' instead of 'dryrun'


```
curl -X POST http://localhost:8080/run -H 'Content-Type:application/json' \
  -d '{
    "target":"avo", 
    "env":"qas",
    "action_name": "delta",
    "action": "delta",
    "is_tag": "latest",
    "options": "-n 1000 -c 1"
    }'
```

Result of this call gives back parameters and result of the openshift commands that are run to delete and create the syncrator pod:
```
{
  "action": "delta",
  "action_name": "delta",
  "env": "qas",
  "is_tag": "latest",
  "openshift_script": "syncrator_run.sh",
  "options": "-n 1000 -c 1",
  "result": "oc login...\nNow using project \"shared-components\" on server \"https://do-prd-okp-m0.do.viaa.be:8443\".\njob.batch \"syncrator-qas-avo-delta\" deleted\njob.batch/syncrator-qas-avo-delta created\n",
  "target": "avo"
}
```



This is the same as the shortcut using defined templates with post call:

```
curl -X POST http://127.0.0.1:8080/delta/avo/qas
```

After executing any job the pod starts up and after some time (approx 13 seconds) you will see it in the jobs table.

```
curl http://syncrator-api-qas-shared-components.apps.do-prd-okp-m0.do.viaa.be/jobs?page=1
```

Example output:
```
[
  {
    "completed": nill,
    "data_source": "mam harvester-AvO",
    "end_time": "Fri, 15 May 2020 15:37:04 GMT",
    "id": 1948,
    "options": "[\"2020-05-14T00:00:00Z\", \"2020-05-16\"]",
    "start_time": "Fri, 15 May 2020 15:36:59 GMT",
    "target_datastore_url": "postgres://dbmaster:o2_Bs8-Nu@postgresql-qas.sc-avo2.svc:5432/avo_qas",
    "total_records": 41,
    "type": "delta",
    "version": "2.4.0"
  },
  ...
```

When the job is finished running completed will be true.

I'm currently working on having current_records also update besides
having total_records so you can have an indication of progress and
we will be adding a seperate table to make the api more robust against concurrent requests. Currently when making a post call to run an actual job
this takes roughly 10 seconds and during that time where pod is starting etc we need to be able to reject new requests for same job parameters.



Delta dryrun example
```
curl -X POST http://syncrator-api-qas-shared-components.apps.do-prd-okp-m0.do.viaa.be/dryrun -H 'Content-Type:application/json' \
  -d '{
    "target":"avo",
    "env":"qas",
    "action_name": "delta",
    "action": "delta",
    "is_tag": "latest",
    "options": "-n 1000 -c 1"
    }'
```

Dryrun result
```
 {
  "ACTION": "delta",
  "ACTION_NAME": "delta",
  "ENV": "qas",
  "IS_TAG": "latest",
  "OPTIONS": "-n 1000 -c 1 --api_job_id dryrun",
  "TARGET": "avo",
  "job_id": "dryrun",
  "result": "oc login https://do-prd-okp-m0.do.viaa.be:8443 -p \"admin\" -u \"admin\" --insecure-skip-tls-verify > /dev/null ; oc project shared-components ; oc delete jobs syncrator-qas-avo-delta ; oc process -f syncrator-openshift/job_template.yaml -p TARGET=\"avo\" -p ENV=\"qas\" -p ACTION_NAME=\"delta\" -p ACTION=\"delta\" -p IS_TAG=\"latest\" -p OPTIONS=\"-n 1000 -c 1 --api_job_id dryrun\" | oc create -f -"
}

```

Now running same job as above for real:

```
curl -X POST http://syncrator-api-qas-shared-components.apps.do-prd-okp-m0.do.viaa.be/run -H 'Content-Type:application/json' \
  -d '{
    "target":"avo",
    "env":"qas",
    "action_name": "delta",
    "action": "delta",
    "is_tag": "latest",
    "options": "-n 1000 -c 1"
    }'
```

output:
```
{
  "action": "delta",
  "action_name": "delta",
  "api_job_id": 20,
  "env": "qas",
  "is_tag": "latest",
  "options": "-n 1000 -c 1",
  "result": "starting",
  "target": "avo"
}

```


Checking status of above job with id 8:
```
 curl http://syncrator-api-qas-shared-components.apps.do-prd-okp-m0.do.viaa.be/jobs/20
{
  "created_at": "Tue, 19 May 2020 11:53:49 GMT",
  "env": "qas",
  "id": 20,
  "job_type": "delta",
  "status": "starting",
  "sync_id": null,
  "target": "avo",
  "updated_at": "Tue, 19 May 2020 11:53:49 GMT"
}
```

When pod is started, status will update and sync_id is filled in and then you see this
as result on the /jobs/8 call:

```
curl http://syncrator-api-qas-shared-components.apps.do-prd-okp-m0.do.viaa.be/jobs/20
{
  "created_at": "Wed, 20 May 2020 16:27:27 GMT",
  "env": "qas",
  "id": 20,
  "job_type": "delta",
  "status": "starting",
  "sync_id": 1989,
  "sync_job": {
    "completed": true,
    "data_source": "mam harvester-AvO",
    "end_time": "Wed, 20 May 2020 18:28:13 GMT",
    "id": 1989,
    "options": "[\"2020-05-19T00:00:00Z\", \"2020-05-21\"]",
    "start_time": "Wed, 20 May 2020 18:28:10 GMT",
    "target_datastore_url": "postgres://<FILTERED>@postgresql-qas.sc-avo2.svc:5432/avo_qas",
    "total_records": 20,
    "type": "delta",
    "version": "2.4.0"
  },
  "target": "avo",
  "updated_at": "Wed, 20 May 2020 16:27:27 GMT"
}
```


If you notice a pod is crashing or you want to cancel a run midway you can call delete on a job
this sets status to deleted and removes the pods that we're started with a previous run/delta/delete/diff call.

example:

```
curl -X DELETE http://syncrator-api-qas-shared-components.apps.do-prd-okp-m0.do.viaa.be/jobs/9
{
  "created_at": "Tue, 19 May 2020 16:26:26 GMT",
  "env": "qas",
  "id": 9,
  "job_type": "diff",
  "status": "deleted",
  "sync_id": null,
  "target": "avo",
  "updated_at": "Tue, 19 May 2020 16:26:26 GMT"
}
```


```
 curl -X POST http://syncrator-api-qas-shared-components.apps.do-prd-okp-m0.do.viaa.be/run -H 'Content-Type:application/json' \
  -d '{
    "target":"avo",
    "env":"qas",
    "action_name": "delete",
    "action": "delete",
    "is_tag": "latest",
    "options": "--debug"
    }'
{
  "ACTION": "delete",
  "ACTION_NAME": "delete",
  "ENV": "qas",
  "IS_TAG": "latest",
  "OPTIONS": "--debug --api_job_id 21",
  "TARGET": "avo",
  "job_id": 21,
  "result": "starting"
}
```



### Testing coverage.

use the scripts/coverage helper to show testing coverage report. You can open htmlcov dir in browser and see detailed report.

```
(python_env) ➜  syncrator-api git:(development) ✗ scripts/coverage
================================================================================ test session starts ================================================================================
platform darwin -- Python 3.7.6, pytest-5.4.1, py-1.8.1, pluggy-0.13.1
rootdir: /Users/wschrep/FreelanceWork/VIAA/syncrator-api
plugins: cov-2.8.1
collected 20 items

tests/test_app.py ....................                                                                                                                                        [100%]

---------- coverage: platform darwin, python 3.7.6-final-0 -----------
Name                     Stmts   Miss  Cover
--------------------------------------------
app/__init__.py              0      0   100%
app/config.py               22      0   100%
app/models.py               62      4    94%
app/openshift_utils.py      47      4    91%
app/run_worker.py           15      0   100%
app/syncrator_api.py       102      8    92%
--------------------------------------------
TOTAL                      248     16    94%


================================================================================ 20 passed in 0.89s =================================================================================
```
