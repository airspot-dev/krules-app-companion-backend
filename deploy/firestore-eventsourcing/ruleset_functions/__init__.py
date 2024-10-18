from datetime import datetime, timezone, timedelta

from krules_core.base_functions.processing import ProcessingFunction
from krules_core.providers import subject_factory

import os

import firebase_admin
from firebase_admin import firestore as firestore_client

from common.event_types import SystemEventsV1

firebase_admin.initialize_app()
db = firestore_client.Client(project=os.environ["FIRESTORE_PROJECT_ID"], database=os.environ["FIRESTORE_DATABASE"])


class GetExpireDateFromTTL(ProcessingFunction):

    def execute(self, payload_dest: str):
        subscription = self.payload.get("subscription")
        group = self.payload.get("group")
        schema = subject_factory(f"schema|{subscription}|{group}")
        ttl = schema.get("ttl", default={"hours": 1})
        self.payload[payload_dest] = datetime.now(timezone.utc) + timedelta(**ttl)


class EventsourceStore(ProcessingFunction):

    def execute(self, expire_date):

        subscription = self.payload.get("subscription")
        group = self.payload.get("group")
        entity_id = self.payload.get("id")
        state = self.payload.get("state")
        changed_properties = self.payload.get("changed_properties")
        datetime_ = state.pop("_last_update", datetime.now(timezone.utc))

        db.collection(f"{subscription}/groups/{group}/{entity_id}/event_sourcing").add({
            "datetime": datetime_,
            "expire_date": expire_date,
            "entity_id": entity_id,
            "state": state,
            "changed_properties": changed_properties,
        })