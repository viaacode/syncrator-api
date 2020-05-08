require 'net/http'
require 'json'

APP = ARGV[0]
ENVIRONMENT = ARGV[1]

OS_URL = 'https://do-prd-okp-m0.do.viaa.be:8443'
PROJECT_NAME = 'shared-components'
BASE_SOLR_URL = "http://solr-#{ENVIRONMENT}-catalogi.apps.do-prd-okp-m0.do.viaa.be/solr/"
CONTENT_TYPE = "-H 'Content-type:text/xml; charset=utf-8'"
SOLR_URL = "#{BASE_SOLR_URL}%{command}&wt=json"

PRIMARY_ALIAS = "#{APP}"
SYNC_ALIAS = "#{APP}-sync"
STANDBY_ALIAS = "#{APP}-standby"

COMMAND_TEMPLATE = {
  list_aliases: 'admin/collections?action=LISTALIASES',
  modify_alias: 'admin/collections?action=CREATEALIAS&name=%{name}&collections=%{collections}'
}

def modify_alias(name, collections)
  puts "MODIFY: #{name} #{collections}"
  uri = URI(
    SOLR_URL % {
      command: (COMMAND_TEMPLATE[:modify_alias] % { name: name, collections: collections.join(',') })
    }
  )
  Net::HTTP.get_response(uri)
end

def init_oc
  system "oc login #{OS_URL}"
  system "oc project #{PROJECT_NAME}"
end

def verify_same_collections(alias1, alias2)
  list_collections_of_alias(alias1) == list_collections_of_alias(alias2)
end

def list_aliases
  uri = URI(SOLR_URL % { command: COMMAND_TEMPLATE[:list_aliases] })
  res = Net::HTTP.get_response(uri)
  JSON.parse(res.body)['aliases']
end

def list_collections_of_alias(name)
  puts "list collections of alias #{name}"
  collections = list_aliases[name].split(',')
  puts "#{collections}"
  collections
end

def delete_standby
  puts 'Deleting standby Solr before sync'
  puts '========================'
  solr_url = BASE_SOLR_URL + STANDBY_ALIAS
  system "curl #{solr_url}/update --data '<delete><query>*:*</query></delete>' #{CONTENT_TYPE}"
  system "curl #{solr_url}/update --data '<commit/>' #{CONTENT_TYPE}"
end

init_oc

raise 'Error: backup is same as primary' if verify_same_collections(PRIMARY_ALIAS, STANDBY_ALIAS)

# sync_to_standby
delete_standby
modify_alias(SYNC_ALIAS, list_collections_of_alias(STANDBY_ALIAS))

raise 'Error: -sync tag is still on primary, not on backup' unless verify_same_collections(SYNC_ALIAS, STANDBY_ALIAS)

system "sh syncrator_sync.sh #{APP} #{ENVIRONMENT}"
