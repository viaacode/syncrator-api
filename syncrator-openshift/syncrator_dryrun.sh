#!/bin/bash
#set -x
TARGET=$1       # values avo, cataloguspro, metadatacatalogus
ENV=$2          # values qas or prd
ACTION_NAME=$3  # values sync, delta, delete, diff
ACTION=$4 
IS_TAG=$5
OPTIONS=$6


OS_URL='https://do-prd-okp-m0.do.viaa.be:8443'
PROJECT_NAME='shared-components'

# this is a dryrun version that does not actually start the job on openshift
# but it generates and shows the template that would run on an actual call
create_template()
{
  TEMPLATE=$1
  echo "oc process -f $TEMPLATE -p TARGET=$TARGET -p ENV=$ENV -p ACTION_NAME=$ACTION_NAME -p ACTION=$ACTION -p IS_TAG=$IS_TAG -p OPTIONS=$OPTIONS | oc create -f -"

  echo ""
  echo "parametrised template:"
  echo "======================"

  # the cat EOF shows the template literally, remove initial tab to show
  # contents correctly with replaced variables from above
  eval "cat <<EOF
$(<./$TEMPLATE)
  EOF
  " 2> /dev/null

}

create_job()
{
  FILE=$1
  create_template job_template.yaml
}

delete_job()
{
  FILE=$1
  echo "oc delete jobs syncrator-${ENV}-${FILE}"
}

if [ "$ENV" = "" ]; then
  printf '%s\n' "No environment given" >&2
  exit 1
fi

start_syncrator_job(){
  delete_job ${TARGET}-${ACTION_NAME}
  create_job ${TARGET}-${ACTION_NAME}
}

echo ""
echo "Syncrator DRYRUN:"
echo "================="

# Dryrun only prints what will be done
echo "oc login $OS_URL"
echo "oc project $PROJECT_NAME"

start_syncrator_job

