#!/bin/bash
#set -x
APP=$1 # Change if needed to cataloguspro/metadatacatalogus
ENVIRONMENT=$2 # Change if needed to qas/prd
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
  create_template job_sync_template.yaml public_params/jobs/${ENVIRONMENT}/${FILE}.public_params
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

syncrator_sync(){
  delete_job ${APP}-sync
  create_job ${APP}-sync
}

# Start sync job
# oc login $OS_URL
oc login $OS_URL -p 'admin' -u 'admin' --insecure-skip-tls-verify
oc project $PROJECT_NAME
syncrator_sync

#<doc><field name="id">1</field></doc>




