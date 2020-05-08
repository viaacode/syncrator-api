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

    `$ curl -v -X GET localhost:8080/health/live`

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

To build the docker containers:

```
scripts/build
```

During development you can autoformat using scripts/autopep
