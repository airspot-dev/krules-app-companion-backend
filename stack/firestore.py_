import pulumi
import pulumi_gcp as gcp
from . import firestore_project_id, firestore_location, firestore_db_name

firestore_db = gcp.firestore.Database(
    "firestore-db",
    name=firestore_db_name,
    project=firestore_project_id,
    location_id=firestore_location,
    type="FIRESTORE_NATIVE",
)

pulumi.export('firestore_db', firestore_db)
