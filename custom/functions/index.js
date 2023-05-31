// The Cloud Functions for Firebase SDK to create Cloud Functions and triggers.
const {logger} = require("firebase-functions");
const {onRequest} = require("firebase-functions/v2/https");
const {onDocumentWritten} = require("firebase-functions/v2/firestore");

// The Firebase Admin SDK to access Firestore.
const {firebase} = require("firebase-admin");
const {initializeApp} = require("firebase-admin/app");
const {getFirestore} = require("firebase-admin/firestore");
const {setGlobalOptions} = require("firebase-functions/v2")
const {config} = require("config")
const {PubSub} = require('@google-cloud/pubsub');

initializeApp();

setGlobalOptions(config);


exports.storeEventSourcing = onDocumentWritten("/{subscription}/groups/{groupName}/{entityId}", async (event) => {
  const value = event.data.after.data();
  const old_value = event.data.before.data();
  const update_mask = []
  const keys = Object.keys(value)
  for (let i = 0; i < keys.length; i++) {
      let key = keys[i];
      if(key !== "LAST_UPDATE" && !old_value.hasOwnProperty(key) || value[key] !== old_value[key]) {
        update_mask.push(key)
      }
  }

  await getFirestore()
      .collection(event.params.subscription + "/groups/" + event.params.groupName + "/" + event.params.entityId + "/event_sourcing")
      .add(
          {
              "state": value,
              "changed_properties": update_mask,
              "entity_id": event.params.entityId,
              "datetime": event.data.after.updateTime.toDate().toISOString().replace("Z", "+00:00")
          }
      );
});
