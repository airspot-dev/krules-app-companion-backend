from firebase_admin import credentials, firestore
import firebase_admin
from krules_core.base_functions import ProcessingFunction
from datetime import datetime
import re

from krules_core.providers import subject_factory

from common.event_types import SUBJECT_PROPERTIES_DATA

FIREBASE_CREDENTIALS_PATH = "/var/secrets/firebase/firebase-auth"

cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)


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


class WriteDocument(ProcessingFunction):

    def execute(self, collection, data, document=None, subject_dest=None, track_last_update=False):

        db = firestore.client()
        if track_last_update:
            data["LAST_UPDATE"] = datetime.now().isoformat()
        if document is not None:
            doc_ref = db.collection(collection).document(document)
            doc_ref.set(data, merge=True)
        else:
            _, doc_ref = db.collection(collection).add(data)
        if subject_dest is not None:
            current_state = doc_ref.get().to_dict()
            if track_last_update:
                current_state.pop("LAST_UPDATE")
            self.subject.set(subject_dest, current_state)


class WriteGroupColumns(ProcessingFunction):

    def execute(self, subscription, group, columns):
        db = firestore.client()
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


class RouteSubjectPropertiesData(ProcessingFunction):

    def execute(self, subscription, group, data, entities_filter=None):

        db = firestore.client()
        if entities_filter is not None:
            docs = db.collection(f"{subscription}/groups/{group}").where(entities_filter).stream()
        else:
            docs = db.collection(f"{subscription}/groups/{group}").stream()
        for doc in docs:
            # if entities_filter is None or re.match(entities_filter, doc.id):
            self.router.route(
                subject=f"entity|{subscription}|{group}|{doc.id}",
                event_type=SUBJECT_PROPERTIES_DATA,
                payload=data
            )


class DeleteDocument(ProcessingFunction):

    def execute(self, collection, document):

        db = firestore.client()
        doc = db.collection(collection).document(document)
        for col in doc.collections():
            delete_collection(col)
        doc.delete()


class DeleteCollection(ProcessingFunction):

    def execute(self, collection):

        db = firestore.client()
        delete_collection(db.collection(collection))
