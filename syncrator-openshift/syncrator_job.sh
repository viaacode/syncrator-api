#!/bin/bash
#set -x
APP=$1 # Change if needed to cataloguspro/metadatacatalogus
ENVIRONMENT=$2 # Change if needed to qas/prd
TYPE=$3 # sync, delta or delete
OS_URL='https://do-prd-okp-m0.do.viaa.be:8443'
PROJECT_NAME='shared-components'

create_template()
{
  TEMPLATE=$1
  PARAMS=$2
  oc process -f $TEMPLATE --param-file=$PARAMS  | oc create -f -
}

create_job()
{
  FILE=$1
  create_template job_template.yaml job_params/${ENVIRONMENT}/${FILE}.public_params
}

delete_job()
{
  FILE=$1
  oc delete jobs syncrator-${ENVIRONMENT}-${FILE}
}

if [ "$ENVIRONMENT" = "" ]; then
  printf '%s\n' "No environment given, e.g. sh init.sh qas" >&2
  exit 1
fi

start_syncrator_job(){
  delete_job ${APP}-${TYPE}
  create_job ${APP}-${TYPE}
}

# Start sync job
echo "oc login..."
oc login $OS_URL -p 'admin' -u 'admin' --insecure-skip-tls-verify > /dev/null
oc project $PROJECT_NAME

start_syncrator_job 

