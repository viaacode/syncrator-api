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

create_job()
{
  FILE=$1
  create_template job_sync_template.yaml public_params/jobs/${ENVIRONMENT}/${FILE}.public_params
}

create_cronjob()
{
  FILE=$1
  create_template cronjob_template.yaml public_params/cronjobs/${ENVIRONMENT}/${FILE}.public_params
}

openshift_init(){
  create_template init_global_template.yaml init_global.private_params
  create_template init_env_template.yaml init_${ENVIRONMENT}.private_params
  apps=( metadatacatalogus cataloguspro avo )
  for app_name in "${apps[@]}"
  do
    create_cronjob ${app_name}-delete
    create_cronjob ${app_name}-delta
    create_job ${app_name}-sync
  done
}

if [ "$ENVIRONMENT" = "" ]; then
  printf '%s\n' "No environment given, e.g. sh init.sh qas" >&2
  exit 1
fi

oc login $OS_URL
oc project $PROJECT_NAME
openshift_init




