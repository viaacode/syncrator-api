#set -x
ENVIRONMENT=$1
OS_URL='https://do-prd-okp-m0.do.viaa.be:8443'
PROJECT_NAME='shared-components'

create_template()
{
  TEMPLATE=$1
  PARAMS=$2
  oc process -f $TEMPLATE --param-file=$PARAMS  | oc create -f -
}

create_cronjob()
{
  FILE=$1
  create_template cronjob_template.yaml public_params/cronjobs/${ENVIRONMENT}/${FILE}.public_params
}

delete_cronjob()
{
  FILE=$1
  oc delete cronjobs syncrator-${ENVIRONMENT}-${FILE}
}

if [ "$ENVIRONMENT" = "" ]; then
  printf '%s\n' "No environment given, e.g. sh init.sh qas" >&2
  exit 1
fi

openshift_init(){
  apps=( cataloguspro metadatacatalogus avo )
  for app_name in "${apps[@]}"
  do
    delete_cronjob ${app_name}-delta
    delete_cronjob ${app_name}-delete
    create_cronjob ${app_name}-delete
    create_cronjob ${app_name}-delta
  done
}

oc login $OS_URL
oc project $PROJECT_NAME
openshift_init




