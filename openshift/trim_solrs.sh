#set -x
ENVIRONMENT=$1 # Change if needed to qas/prd

# apps=(cataloguspro metadatacatalogus)

# for app_name in "${apps[@]}"
# do
#   SECONDARY_URL="http://solr-${ENVIRONMENT}-catalogi.apps.do-prd-okp-m0.do.viaa.be/solr/${app_name}-sync"
#   # Delete existing records in backup solr
#   echo $app_name
#   echo $ENVIRONMENT
#   echo 'Deleting secondary Solr'
#   echo '========================'
#   curl $SECONDARY_URL/update --data '<delete><query>*:*</query></delete>' -H 'Content-type:text/xml; charset=utf-8'
#   echo 'Committing delete'
#   echo '========================'
#   curl $SECONDARY_URL/update --data '<commit/>' -H 'Content-type:text/xml; charset=utf-8'
# done

CPRO_PRIMARY="http://solr-${ENVIRONMENT}-catalogi.apps.do-prd-okp-m0.do.viaa.be/solr/cataloguspro"
echo 'Trimming primary Solr of CPRO'
echo '========================'
curl $CPRO_PRIMARY/update --data '<delete><query>-licenses_ssim:(VIAA-INTRA_CP-METADATA-ALL OR VIAA-INTRA_CP-CONTENT)</query></delete>' -H 'Content-type:text/xml; charset=utf-8'
echo 'Committing delete'
echo '========================'
curl $CPRO_PRIMARY/update --data '<commit/>' -H 'Content-type:text/xml; charset=utf-8'

MDC_PRIMARY="http://solr-${ENVIRONMENT}-catalogi.apps.do-prd-okp-m0.do.viaa.be/solr/metadatacatalogus"
echo 'Trimming primary Solr of MDC'
echo '========================'
curl $MDC_PRIMARY/update --data '<delete><query>-licenses_ssim:(VIAA-PUBLIEK-METADATA-LTD OR VIAA-PUBLIEK-METADATA-ALL)</query></delete>' -H 'Content-type:text/xml; charset=utf-8'
echo 'Committing delete'
echo '========================'
curl $MDC_PRIMARY/update --data '<commit/>' -H 'Content-type:text/xml; charset=utf-8'
