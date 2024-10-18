import os
from datetime import datetime, timezone
from typing import Dict, Any

from dateutil import parser

import firebase_admin
from firebase_admin import firestore
from krules_core.base_functions.processing import ProcessingFunction
from krules_core.route.router import DispatchPolicyConst

from common.event_types import IngestionEventsV1

# FIREBASE_CREDENTIALS_PATH = "/var/secrets/firebase/firebase-auth"

# cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
# firebase_admin.initialize_app(cred)
firebase_admin.initialize_app()

INGESTION_TOPIC = os.environ["INGESTION_TOPIC"]

def get_readable_name(name):
    return name.replace("-", " ").replace("_", " ").replace(".", " ").replace(":", " ").replace("|", " ").capitalize()


def delete_collection(coll_ref, batch_size=10):
    docs = coll_ref.list_documents(page_size=batch_size)
    deleted = 0

    for doc in docs:
        print(f'Deleting doc {doc.id} => {doc.get().to_dict()}')
        for col in doc.collections():
            delete_collection(col, batch_size)
        doc.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)


def _get_db():
    return firestore.Client(project=os.environ["FIRESTORE_PROJECT_ID"], database=os.environ["FIRESTORE_DATABASE"])

def parse_flexible_datetime(date_string: str) -> datetime:
    # Use dateutil.parser to parse the date string
    return parser.parse(date_string)

def process_dictionary(data: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in data.items():
        if isinstance(value, str) and value.startswith("dt|"):
            try:
                # Extract the datetime part and parse it
                date_string = value[3:]  # Remove the "dt|" prefix
                data[key] = parse_flexible_datetime(date_string)
            except (ValueError, TypeError) as e:
                print(f"Error parsing date string {value}: {e}")
    return data

class WriteDocument(ProcessingFunction):

    def execute(self, collection, data, document=None, subject_dest=None):

        db = _get_db()

        data = process_dictionary(data)
        if "_last_update" not in data:
            data["_last_update"] = datetime.now(timezone.utc)

        if document is not None:
            doc_ref = db.collection(collection).document(document)
            doc_ref.set(data, merge=True)
        else:
            _, doc_ref = db.collection(collection).add(data)
        if subject_dest is not None:
            current_state = doc_ref.get().to_dict()
            current_state.pop("_last_update", None)
            self.subject.set(subject_dest, current_state)


class WriteGroupColumns(ProcessingFunction):

    def execute(self, subscription, group, columns):
        db = _get_db()
        group_doc_ref = db.collection(f"{subscription}/settings/schemas").document(group)
        if not group_doc_ref.get().exists:
            group_doc_ref.set(
                {
                    "readable_name": get_readable_name(group)
                }
            )
        for col in columns:
            col_doc_ref = db.collection(f"{subscription}/settings/schemas/{group}/columns").document(col)
            if not col_doc_ref.get().exists:
                col_doc_ref.set(
                    {
                        "readable_name": get_readable_name(col),
                        "rules": []
                    }
                )


class UpdateDocument(ProcessingFunction):

    def execute(self, collection: str, document: str, data: dict):
        db = _get_db()
        doc_ref = db.collection(collection).document(document)
        doc_ref.update(data)


class RouteSubjectPropertiesData(ProcessingFunction):

    def execute(self, subscription, group, data, entities_filter=None):

        db = _get_db()
        if isinstance(entities_filter, str):
            entities_filter = eval(entities_filter)
        if entities_filter is not None and len(entities_filter) > 0:
            docs = db.collection(f"{subscription}/groups/{group}").where(*entities_filter).stream()
        else:
            docs = db.collection(f"{subscription}/groups/{group}").stream()
        self.payload["entities"] = []
        data = process_dictionary(data)
        if "_last_update" not in data:
            data["_last_update"] = datetime.now(timezone.utc)
        for doc in docs:
            self.payload["entities"].append(f"entity|{subscription}|{group}|{doc.id}")
            self.router.route(
                subject=f"entity|{subscription}|{group}|{doc.id}",
                event_type=IngestionEventsV1.ENTITY_DATA,
                payload={
                    "data": data
                },
                dispatch_policy=DispatchPolicyConst.DIRECT,
                topic=INGESTION_TOPIC,
            )


class DeleteDocument(ProcessingFunction):

    def execute(self, collection, document):

        db = _get_db()
        doc = db.collection(collection).document(document)
        for col in doc.collections():
            delete_collection(col)
        doc.delete()


class DeleteCollection(ProcessingFunction):

    def execute(self, collection):

        db = _get_db()
        delete_collection(db.collection(collection))
