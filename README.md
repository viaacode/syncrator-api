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

1. Start by installing pip packages and setting up environment:
    `scripts/install`

2. Activate the virtual environment:

    `$ source python_env/bin/activate`

4. Run the tests with:

    `$ scripts/test`

5. Run the application:

   `$ scrits/run`

The application is now serving requests on `localhost:8080`. Try it with:

    `$ curl -v -X GET http://127.0.0.1:8080/`


### Running using Docker

1. Build the container and run it:

   `$ scripts/build`

### Helper scripts
To run the tests locally and also run flake8 linter/code checking:
``` 
$ scripts/test
=============================== test session starts ===============================
platform darwin -- Python 3.7.6, pytest-5.4.1, py-1.8.1, pluggy-0.13.1 -- /Users/wschrep/FreelanceWork/VIAA/syncrator-api/python_env/bin/python
cachedir: .pytest_cache
rootdir: /Users/wschrep/FreelanceWork/VIAA/syncrator-api
plugins: recording-0.7.0, cov-2.8.1
collected 24 items

tests/test_app.py::test_home PASSED                                         [  4%]
tests/test_app.py::test_liveness_check PASSED                               [  8%]
tests/test_app.py::test_dryrun_sync_job PASSED                              [ 12%]
tests/test_app.py::test_dryrun_delta_job PASSED                             [ 16%]
tests/test_app.py::test_dryrun_delete_job PASSED                            [ 20%]
tests/test_app.py::test_diff_job_dryrun PASSED                              [ 25%]
tests/test_app.py::test_password_filter_api_job_nested PASSED               [ 29%]
tests/test_app.py::test_list_api_jobs PASSED                                [ 33%]
tests/test_app.py::test_list_sync_jobs_and_pass_filter PASSED               [ 37%]
tests/test_app.py::test_get_unknown_job PASSED                              [ 41%]
tests/test_app.py::test_get_existing_starting_job PASSED                    [ 45%]
tests/test_app.py::test_get_existing_completed_job PASSED                   [ 50%]
tests/test_app.py::test_delete_job PASSED                                   [ 54%]
tests/test_app.py::test_delete_unknown_job PASSED                           [ 58%]
tests/test_app.py::test_param_parsing PASSED                                [ 62%]
tests/test_app.py::test_dryrun_matches_templated_get PASSED                 [ 66%]
tests/test_app.py::test_general_job_run PASSED                              [ 70%]
tests/test_app.py::test_dryrun_openshift_commands PASSED                    [ 75%]
tests/test_app.py::test_random_404 PASSED                                   [ 79%]
tests/test_app.py::test_diff_job PASSED                                     [ 83%]
tests/test_app.py::test_missing_template PASSED                             [ 87%]
tests/test_solr_utils.py::test_solr_preperation PASSED                      [ 91%]
tests/test_solr_utils.py::test_list_aliases PASSED                          [ 95%]
tests/test_solr_utils.py::test_sync_to_standby_calls PASSED                 [100%]

=============================== 24 passed in 0.47s ================================
Running flake8 linter...
ALL OK
```
If tests fail or flake8 gives warnings you will be presented with them here now. The jenkins build won't
fail if there are linter warnings but it's nice to get an 'ALL OK' which means 0 issues found by flake8.
The tests do have to all pass, if one fails the build won't be deployed by the jenkins pipeline.



You can use the scripts/coverage helper to show testing coverage report.
After running it you can open htmlcov/index.html to see a nice detailed report on all code which is tested or missed during tests.

```
$ ==================================== test session starts ====================================
platform darwin -- Python 3.7.6, pytest-5.4.1, py-1.8.1, pluggy-0.13.1
rootdir: /Users/wschrep/FreelanceWork/VIAA/syncrator-api
plugins: recording-0.7.0, cov-2.8.1
collected 25 items                                                                          

tests/test_app.py ....................                                                [ 80%]
tests/test_openshift_utils.py ..                                                      [ 88%]
tests/test_solr_utils.py ...                                                          [100%]

---------- coverage: platform darwin, python 3.7.6-final-0 -----------
Name                     Stmts   Miss  Cover
--------------------------------------------
app/__init__.py              0      0   100%
app/config.py               22      0   100%
app/models.py               61      4    93%
app/openshift_utils.py      47      2    96%
app/run_worker.py           12      0   100%
app/solr_utils.py           49      3    94%
app/syncrator_api.py       107      1    99%
--------------------------------------------
TOTAL                      298     10    97%
Coverage HTML written to dir htmlcov


==================================== 25 passed in 0.66s =====================================
```




To run a server on port 8080:

``` 
$ scripts/run 
```
The root page has links and some minimal description of other available routes for api calls, open in your browser by
following this link <a href="http://127.0.0.1:8080/">Syncrator API</a> after you have the server running.



To build the docker containers:

```
$ scripts/build
```

During development you can autoformat using scripts/autopep and to make changes and see response instantly without restarting the application
theres the scripts/debug helper script now
```
$ scripts/debug
```
It also runs on port 8080 like the scripts/run and docker builds


### API calls available
```
GET /jobs - paginated list of active api started jobs
GET /jobs/<id> - get api job and related sync_job details and progress
DELETE /jobs/<id> - get api job, set status to "deleted" and run openshift oc call to delete any openshift jobs started with these parameters.

GET /sync_jobs - paginated list of all sync jobs (these include syncrator runs started with CRON)

GET /delta/avo/qas - delta synchronisation job dryrun
POST /delta/<project>/<env> - start a new delta synchronisation job

GET /delete/avo/qas - delete synchronisation job dryrun
POST /delete/<project>/<env> - start a new delete synchronisation job

GET /diff/avo/qas - dryrun for delta followed by delete in one go for partial updates
POST /diff/<project>/<env> - start delta job followed by a delete job

GET /sync/avo/qas - full synchronisation job dryrun
POST /sync/<project>/<env> - start a new full synchronisation job

POST /run - start custom syncrator job by passing all template parameters (target, env, action_name, action, is_tag, options)
POST /dryrun - dryrun custom job by passing all template parameters (target, env, action_name, action, is_tag, options)
```


As mentioned in examples the sync, delta, delete (and to be implemented diff) calls can all be done
using the /run and /dryrun post's but you will need to exactly specify the 6 parameters that fill in the template.

### Paremetrised jobs
When using the simplified calls ex /sync/avo/qas or /delta/avo/prd these do a lookup in the parameter files defined 
in the directory 'syncrator-openshift/job_params'.
Here is a list of all currently predefined params: 
```
syncrator-openshift/job_params
├── prd
│   ├── avo-delete.public_params
│   ├── avo-delta.public_params
│   ├── avo-diff.public_params
│   ├── avo-sync.public_params
│   ├── cataloguspro-delete.public_params
│   ├── cataloguspro-delta.public_params
│   ├── cataloguspro-diff.public_params
│   ├── cataloguspro-sync.public_params
│   ├── metadatacatalogus-delete.public_params
│   ├── metadatacatalogus-delta.public_params
│   ├── metadatacatalogus-diff.public_params
│   └── metadatacatalogus-sync.public_params
└── qas
    ├── avo-delete.public_params
    ├── avo-delta.public_params
    ├── avo-diff.public_params
    ├── avo-sync.public_params
    ├── cataloguspro-delete.public_params
    ├── cataloguspro-delta.public_params
    ├── cataloguspro-diff.public_params
    ├── cataloguspro-sync.public_params
    ├── metadatacatalogus-delete.public_params
    ├── metadatacatalogus-delta.public_params
    ├── metadatacatalogus-diff.public_params
    └── metadatacatalogus-sync.public_params

2 directories, 24 files

```


### Authorization

This has been added recently 3/11/2020. For any POST, DELETE call that does actual processing you also need to 
pass an access token in the authorization header. To get a token you first make a request or use the form provided
on the default homepage of this service.

Here is a curl example to get an access token:
```
$ curl -X  POST -F "username=somelogin@meemoo.be" -F "password=PW_HERE" http://localhost:8080/login
 
```

This returns an access token as json response:
```
{
  "access_token": "YOUR_PERSONAL_TOKEN", 
  "expires_in": 899, 
  "token_type": "bearer"
}
```

Then for all the examples below also add this token in an authorization bearer header.
For example a delete job call will become:

```
$ curl -X DELETE -H 'Authorization: Bearer YOUR_PERSONAL_TOKEN' http://localhost:8080/jobs/123
```


### Examples

Example run a full sync on avo project in qas environment as dryrun we first want to see the template output. We use jq to show only the template result:
```
$ curl http://127.0.0.1:8080/sync/avo/qas 
```

To now have an actual syncrator pod startup just make same request but then with a post call:
```
$ curl -X POST http://127.0.0.1:8080/sync/avo/qas
```


If you don't want or don't have a predifined template (.public_params file) you can start a custom syncrator job like so:

```
$ curl -X POST http://localhost:8080/dryrun -H 'Content-Type:application/json' -H 'Authorization: Bearer YOUR_PERSONAL_TOKEN' \
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
$ curl http://127.0.0.1:8080/delta/avo/qas
```

To make the actual pod start and execute the openshift commands use the path 'run' instead of 'dryrun'


Delta dryrun example
```
$ curl -X POST http://syncrator-api-qas-shared-components.apps.do-prd-okp-m0.do.viaa.be/dryrun -H 'Content-Type:application/json' -H 'Authorization: Bearer YOUR_PERSONAL_TOKEN' \
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
$ curl -X POST http://syncrator-api-qas-shared-components.apps.do-prd-okp-m0.do.viaa.be/run -H 'Content-Type:application/json' -H 'Authorization: Bearer YOUR_PERSONAL_TOKEN' \
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
$ curl http://syncrator-api-qas-shared-components.apps.do-prd-okp-m0.do.viaa.be/jobs/20
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
$ curl http://syncrator-api-qas-shared-components.apps.do-prd-okp-m0.do.viaa.be/jobs/20
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
$ curl -X DELETE http://syncrator-api-qas-shared-components.apps.do-prd-okp-m0.do.viaa.be/jobs/9 -H 'Authorization: Bearer YOUR_PERSONAL_TOKEN'
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


### Complete run with progress checking example:

Start actual syncrator sync job with progress by calling it with a post request:

```
$ curl -X POST http://syncrator-api-qas-shared-components.apps.do-prd-okp-m0.do.viaa.be/sync/avo/qas -H 'Authorization: Bearer YOUR_PERSONAL_TOKEN'
{
  "ACTION": "sync",
  "ACTION_NAME": "sync",
  "ENV": "qas",
  "IS_TAG": "latest",
  "OPTIONS": "-n 1000 -c 1 --api_job_id 34",
  "TARGET": "avo",
  "job_id": 34,
  "result": "starting"
}
```


We notice job_id is 34 and can fetch it status (also if we would post again while it's running we would just get back the same job_id because
syncrator-api sees that a similar job is already running);
Fetching status, by going to /jobs/<job_id>
```
$ curl http://syncrator-api-qas-shared-components.apps.do-prd-okp-m0.do.viaa.be/jobs/34
{
  "created_at": "Fri, 22 May 2020 14:30:35 GMT",
  "env": "qas",
  "id": 34,
  "job_type": "sync",
  "status": "starting",
  "sync_id": null,
  "target": "avo",
  "updated_at": "Fri, 22 May 2020 14:30:35 GMT"
}
```

This means the openshift commands are running and pod is starting up.

Waiting a few more seconds we then get this (status running and sync_id is filled in meaning the syncrator pod is now started
correctly and running the specified job). For delete, diff and delta jobs this goes really fast in under a minute most of the time, 
however a sync job lasts 15 to 20 minutes before reaching complete status.

```
$ curl http://syncrator-api-qas-shared-components.apps.do-prd-okp-m0.do.viaa.be/jobs/34

{
  "created_at": "Fri, 22 May 2020 18:11:44 GMT",
  "env": "qas",
  "id": 34,
  "job_type": "sync",
  "status": "running",
  "sync_id": 2017,
  "sync_job": {
    "completed": null,
    "data_source": "mam harvester-AvO",
    "end_time": null,
    "id": 2017,
    "options": "[nil, nil]",
    "start_time": "Fri, 22 May 2020 20:12:12 GMT",
    "target_datastore_url": "postgres://<FILTERED>@postgresql-qas.sc-avo2.svc:5432/avo_qas",
    "total_records": 0,
    "type": "sync",
    "version": "2.4.0"
  },
  "target": "avo",
  "updated_at": "Fri, 22 May 2020 18:11:44 GMT"
}
```

Job status is now running and the sync_id is also finished, so we get back the progress of the actual sync_job also. 
We wait a little longer, make another request:

```
$ curl http://syncrator-api-qas-shared-components.apps.do-prd-okp-m0.do.viaa.be/jobs/34

{
  "created_at": "Fri, 22 May 2020 18:11:44 GMT", 
  "env": "qas", 
  "id": 34, 
  "job_type": "sync", 
  "status": "completed", 
  "sync_id": 2017, 
  "sync_job": {
    "completed": true, 
    "data_source": "mam harvester-AvO", 
    "end_time": "Fri, 22 May 2020 20:21:35 GMT", 
    "id": 2017, 
    "options": "[nil, nil]", 
    "start_time": "Fri, 22 May 2020 20:12:12 GMT", 
    "target_datastore_url": "postgres://<FILTERED>@postgresql-qas.sc-avo2.svc:5432/avo_qas", 
    "total_records": 19945, 
    "type": "sync", 
    "version": "2.4.0"
  }, 
  "target": "avo", 
  "updated_at": "Fri, 22 May 2020 18:11:44 GMT"
}
```
We see job status is now completed here. all went well the syncrator pod finished. If we call the above POST request again we now see a new pod will be started again and
the whole cycle repeats.
If anything goes wrong status will be 'failed' this is set by syncrator itself when api_job_id is passed you may also do another post or delete the job in this case.

