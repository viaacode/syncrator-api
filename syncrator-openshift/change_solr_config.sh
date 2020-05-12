# see https://lucene.apache.org/solr/guide/6_6/config-api.html#config-api

APP=$1 # Change if needed to cataloguspro/metadatacatalogus
ENVIRONMENT=$2 # Change if needed to qas/prd

NOT_SYNCED_URL="http://solr-${ENVIRONMENT}-catalogi.apps.do-prd-okp-m0.do.viaa.be/solr/${APP}"


curl $NOT_SYNCED_URL/config -H 'Content-type:application/json'  -d '{
  "set-property": {
    "updateHandler.autoCommit.maxTime":120000,
    "updateHandler.autoCommit.maxDocs":1000,
    "updateHandler.autoSoftCommit.maxTime":600000
  }
}'

curl $NOT_SYNCED_URL/config/overlay
