from firebase_admin import credentials, firestore
import firebase_admin
from krules_core.base_functions import ProcessingFunction

FIREBASE_CREDENTIALS_PATH = "/var/secrets/firebase/firebase-auth"

cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)


def get_readable_name(name):
    return name.replace("-", " ").replace("_", " ").replace(".", " ").replace(":", " ").replace("|", " ").capitalize()


class WriteDocument(ProcessingFunction):

    def execute(self, collection, document, data, subject_dest=None):

        db = firestore.client()
        doc_ref = db.collection(collection).document(document)
        doc_ref.set(data, merge=True)
        if subject_dest is not None:
            self.subject.set("current_state", doc_ref.get().to_dict())


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
