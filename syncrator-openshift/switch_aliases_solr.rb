require 'net/http'
require 'json'

APP = ARGV[0]
ENVIRONMENT = ARGV[1]

OS_URL = 'https://do-prd-okp-m0.do.viaa.be:8443'
PROJECT_NAME = 'shared-components'
BASE_SOLR_URL = "http://solr-#{ENVIRONMENT}-catalogi.apps.do-prd-okp-m0.do.viaa.be/solr/"
SOLR_URL = "#{BASE_SOLR_URL}%{command}&wt=json"

PRIMARY_ALIAS = "#{APP}"
SYNC_ALIAS = "#{APP}-sync"
STANDBY_ALIAS = "#{APP}-standby"

COMMAND_TEMPLATE = {
  list_aliases: 'admin/collections?action=LISTALIASES',
  modify_alias: 'admin/collections?action=CREATEALIAS&name=%{name}&collections=%{collections}'
}

def modify_alias(name, collections)
  uri = URI(
    SOLR_URL % {
      command: (COMMAND_TEMPLATE[:modify_alias] % { name: name, collections: collections.join(',') })
    }
  )
  Net::HTTP.get_response(uri)
end

def list_aliases
  uri = URI(SOLR_URL % { command: COMMAND_TEMPLATE[:list_aliases] })
  res = Net::HTTP.get_response(uri)
  JSON.parse(res.body)['aliases']
end

def list_collections_of_alias(name)
  collections = list_aliases[name].split(',')
  puts "LIST alias: #{name} has collections: #{collections}"
  collections
end

def switch_primary_and_backup
  standby_collection = list_collections_of_alias(STANDBY_ALIAS)
  primary_collection = list_collections_of_alias(PRIMARY_ALIAS)
  modify_alias(PRIMARY_ALIAS, standby_collection)
  modify_alias(STANDBY_ALIAS, primary_collection)
end

standby_collection = list_collections_of_alias(STANDBY_ALIAS)
primary_collection = list_collections_of_alias(PRIMARY_ALIAS)

if standby_collection.size == 1 && primary_collection.size == 1
  switch_primary_and_backup
  system "curl #{BASE_SOLR_URL}#{PRIMARY_ALIAS}/update --data '<commit/>' -H 'Content-type:text/xml; charset=utf-8'"
  puts 'LIST all aliases:'
  puts list_aliases
end
