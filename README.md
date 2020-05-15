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
================================================================================ test session starts ================================================================================
platform darwin -- Python 3.7.6, pytest-5.4.1, py-1.8.1, pluggy-0.13.1 -- /Users/wschrep/FreelanceWork/VIAA/syncrator-api/python_env/bin/python
cachedir: .pytest_cache
rootdir: /Users/wschrep/FreelanceWork/VIAA/syncrator-api
plugins: cov-2.8.1
collected 5 items

tests/test_app.py::test_home PASSED                                                                                                                                           [ 20%]
tests/test_app.py::test_liveness_check PASSED                                                                                                                                 [ 40%]
tests/test_app.py::test_start_job PASSED                                                                                                                                      [ 60%]
tests/test_app.py::test_list_jobs PASSED                                                                                                                                      [ 80%]
tests/test_app.py::test_get_job PASSED                                                                                                                                        [100%]

================================================================================= 5 passed in 0.19s =================================================================================
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

(python_env) ➜  syncrator-api git:(development) ✗ scripts/debug
 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
{"message": " * Running on http://127.0.0.1:8080/ (Press CTRL+C to quit)"}
{"message": " * Restarting with stat"}
{"message": " * Debugger is active!"}
{"message": " * Debugger PIN: 119-009-382"}

```
It also runs on port 8080 like the scripts/run and docker builds


### Usage

Example:
```
curl http://127.0.0.1:8080/sync/avo/qas | jq .result -r
```


Just do the dryrun generic call like this:

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

This has the same result as doing following request:
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

This is the same as the shortcut using defined templates with post call:

```
curl -X POST http://127.0.0.1:8080/delta/avo/qas
```

### API calls
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


