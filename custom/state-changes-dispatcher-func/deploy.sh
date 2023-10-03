gcloud functions deploy state-changes-dispatcher --project airspot-krules-companion-dev --region europe-west6 \
  --entry-point index \
  --runtime python311 \
  --set-env-vars URMET_WALLBOX_TOPIC="projects/urmet-wallbox-dev/topics/urmet-wallbox-ocpp-companion-dev1" \
  --set-env-vars COLDCHAIN_ITEMS_TOPIC="projects/airspot-comp-coldchain-dev/topics/ingestion" \
  --set-env-vars COLDCHAIN_LOCATIONS_TOPIC="projects/airspot-comp-coldchain-dev/topics/ingestion-locations" \
  --trigger-event "providers/cloud.firestore/eventTypes/document.write" \
  --trigger-resource "projects/airspot-krules-companion-dev/databases/(default)/documents/{subscription}/groups/{group_id}/{entity_id}"
