#!/bin/bash
#set -x
APP=$1 # Change if needed to cataloguspro/metadatacatalogus
ENVIRONMENT=$2 # Change if needed to qas/prd
TYPE=$3 # sync, delta or delete
OS_URL='https://do-prd-okp-m0.do.viaa.be:8443'
PROJECT_NAME='shared-components'

# this is a dryrun version that does not actually start the job on openshift
# but it generates and shows the template that would run on an actual call
create_template()
{
  TEMPLATE=$1
  PARAMS=$2
  # oc process -f $TEMPLATE --param-file=$PARAMS  | oc create -f -
  echo "oc process -f $TEMPLATE --param-file=$PARAMS | oc create -f -"

  echo ""
  echo "params file:"
  echo "============"

  while read line
  do
      eval echo "$line"
  done < "./$PARAMS"

  # load param variable into memory so template can substitute them
  source "./$PARAMS"

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
  create_template job_template.yaml job_params/${ENVIRONMENT}/${FILE}.public_params
}

delete_job()
{
  FILE=$1
  echo "oc delete jobs syncrator-${ENVIRONMENT}-${FILE}"
}

if [ "$ENVIRONMENT" = "" ]; then
  printf '%s\n' "No environment given, e.g. sh init.sh qas" >&2
  exit 1
fi

start_syncrator_job(){
  delete_job ${APP}-${TYPE}
  create_job ${APP}-${TYPE}
}

echo "Syncrator DRYRUN:"
echo "================="

# Dryrun only prints what will be done
echo "oc login $OS_URL"
echo "oc project $PROJECT_NAME"

start_syncrator_job

