from krules_core.base_functions.filters import *
from krules_core.base_functions.processing import *
from krules_core.event_types import SubjectPropertyChanged
from krules_core.models import Rule
from krules_core.providers import subject_factory

from common.event_types import IngestionEventsV1
from firestore import WriteDocument, WriteGroupColumns, RouteSubjectPropertiesData, DeleteDocument, DeleteCollection, \
    UpdateDocument


class SubjectSchemaUpdateGroupColumns(ProcessingFunction):

    def execute(self, subscription, group, current_state):
        subject = subject_factory(f'schema|{subscription}|{group}', use_cache_default=False)
        subject.set("columns", lambda v: sorted(list(set((v or []) + [k for k in current_state if not k.startswith("_")]))))
        self.payload["columns"] = subject.get("columns")
        subject.store()


rulesdata: List[Rule] = [
    Rule(
        name="ingestion-multi-receiver",
        subscribe_to=[IngestionEventsV1.GROUP_DATA],
        description=
        """
            Pub/Sub multi message receiver from ingestion channels
        """,
        filters=[
            SubjectNameMatch("^group[|](?P<subscription>.+)[|](?P<group>.+)$", payload_dest="base_info"),
            Filter(lambda payload: "data" in payload and isinstance(payload["data"], dict) and len(payload["data"]))
        ],
        processing=[
            RouteSubjectPropertiesData(
                subscription=lambda payload: payload["base_info"]["subscription"],
                group=lambda payload: payload["base_info"]["group"],
                data=lambda payload: payload["data"],
                entities_filter=lambda payload: payload["entities_filter"],
            )
        ]
    ),
    Rule(
        name="ingestion-first-receiver",
        subscribe_to=[IngestionEventsV1.ENTITY_DATA],
        description=
        """
            Pub/Sub message receiver from ingestion channels
        """,
        filters=[
            SubjectNameMatch("^entity[|](?P<subscription>.+)[|](?P<group>.+)[|](?P<id>.+)$",
                             payload_dest="entity_base_info"),
            Filter(lambda payload: "data" in payload and isinstance(payload["data"], dict) and len(payload["data"]))
        ],
        processing=[
            WriteDocument(
                collection=lambda payload:
                f"{payload['entity_base_info']['subscription']}/groups/{payload['entity_base_info']['group']}",
                document=lambda payload: payload['entity_base_info']['id'],
                data=lambda payload: payload["data"],
            ),
            SubjectSchemaUpdateGroupColumns(
                subscription=lambda payload: payload["entity_base_info"]["subscription"],
                group=lambda payload: payload["entity_base_info"]["group"],
                current_state=lambda payload: payload["data"],
            ),
        ]
    ),
    Rule(
        name="update-group-columns",
        subscribe_to=[SubjectPropertyChanged],
        description=
        """
        On property changed update group columns
        """,
        filters=[
            SubjectNameMatch(
                "^schema[|](?P<subscription>.+)[|](?P<group>.+)$",
                payload_dest="entity_base_info"
            ),
            OnSubjectPropertyChanged("columns")
        ],
        processing=[
            WriteGroupColumns(
                subscription=lambda payload: payload['entity_base_info']['subscription'],
                group=lambda payload: payload['entity_base_info']['group'],
                columns=lambda payload: payload["value"],
            )
        ]
    ),
    Rule(
        name="delete-group",
        subscribe_to=[IngestionEventsV1.GROUP_DELETE],
        description=
        """
        Delete group
        """,
        filters=[
            SubjectNameMatch(
                "^group[|](?P<subscription>.+)[|](?P<group>.+)$",
                payload_dest="entity_base_info"
            ),
        ],
        processing=[
            UpdateDocument(
                collection=lambda payload: f"{payload['entity_base_info']['subscription']}/settings/schemas",
                document=lambda payload: payload['entity_base_info']['group'],
                data={"_deleting": True}
            ),
            DeleteCollection(
                collection=lambda payload:
                f"{payload['entity_base_info']['subscription']}/groups/{payload['entity_base_info']['group']}"
            ),
            Process(
                lambda payload: subject_factory(f"schema|{payload['entity_base_info']['subscription']}|{payload['entity_base_info']['group']}").flush()
            ),
            DeleteDocument(
                collection=lambda payload: f"{payload['entity_base_info']['subscription']}/settings/schemas",
                document=lambda payload: payload['entity_base_info']['group']
            ),
            FlushSubject()
        ]
    ),
    Rule(
        name="delete-entity",
        subscribe_to=[IngestionEventsV1.ENTITY_DELETE],
        description=
        """
        Delete entity
        """,
        filters=[
            SubjectNameMatch(
                "^entity[|](?P<subscription>.+)[|](?P<group>.+)[|](?P<id>.+)$",
                payload_dest="entity_base_info"
            ),
        ],
        processing=[
            UpdateDocument(
                collection=lambda payload: f"{payload['entity_base_info']['subscription']}/groups/{payload['entity_base_info']['group']}",
                document=lambda payload: payload['entity_base_info']['id'],
                data={"_deleting": True}
            ),
            DeleteDocument(
                collection=lambda payload: f"{payload['entity_base_info']['subscription']}/groups/{payload['entity_base_info']['group']}",
                document=lambda payload: payload['entity_base_info']['id']
            ),
            FlushSubject(),
        ]
    ),
]
