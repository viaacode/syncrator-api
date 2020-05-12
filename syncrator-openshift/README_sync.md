# Syncing

Run `resync_solr.rb` (change APP en ENVIRONMENT parameters if required)

**Manual:**

Check if the sync was successful on NOT_SYNCED_URL (the -standby collection).
This ensures that no errors occured and that labels can be switched safely.

If the sync was successful, run `switch_aliases_solr.rb` (this switches the
aliases 'app' and 'app-standby' between the two Solrs and points the -sync to
'app'). The services will automatically pick up the correct version.


**Solr setup (for deeper understanding)**

Setup die ik nu voor ogen heb voor CPRO (MDC is gelijkaardig).

**Replicas:**

- solr-01-qas
- solr-02-qas

**Collections:**

- cataloguspro-1
- cataloguspro-2

**Aliases:**

- cataloguspro (wijst naar synced collection, alternerend -1 of -2)
- cataloguspro-sync (wijst naar collection die gesynced moet worden, meestal de
  niet standby aka alias cataloguspro)
- cataloguspro-standby (wijst naar backup/out of sync collection, alternerend
  -1 of -2, tegenovergesteld van cataloguspro)

**Voor rebuild/resync:**

- standby wissen
- sync richten op -standby

**Na rebuild/resync:**

Alias cataloguspro en cataloguspro-standby switchen (sync is dan ook  gericht
op de niet standby)

**Config:**

Syncrator delta verwijst altijd naar cataloguspro-sync Syncrator sync verwijst
altijd naar cataloguspro-sync Cataloguspro verwijst altijd naar cataloguspro
(edited) 

(Idem voor Metadatacatalogus)

Voor AVO:

bv: openshift map -> sh syncrator_sync.sh avo qas

Dit neemt de laatste config uit config_maps op openshift. Wil je bv archief.be
als mediahaven url voor avo op qas maar niet voor solr dan kun je de mam_url
weghalen uit syncrator-target-qas en ze toevoegen aan elke
syncrator-envtarget-${ENV}-${TARGET} config map en dan de url weer veranderen
naar archief.be voor syncrator-envtarget-qas-avo. Bij mijn weten overschrijft
openshift geen ENV variables maar geeft gewoon een error als je ze twee keer
instelt. 

- configMapRef:  
  name: syncrator-global
- configMapRef:  
  name: syncrator-env-${ENV}
- configMapRef:  
  name: syncrator-target-${TARGET}
- configMapRef:  
  name: syncrator-envtarget-${ENV}-${TARGET}
