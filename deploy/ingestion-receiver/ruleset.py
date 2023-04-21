from krules_core.base_functions import *
from krules_core.models import Rule
from krules_core.event_types import SubjectPropertyChanged
from firestore import WriteDocument, WriteGroupColumns, RouteSubjectPropertiesData, DeleteDocument, DeleteCollection
from common.event_types import ENTITY_STATE_CHANGED, SUBJECT_PROPERTIES_DATA, SUBJECT_PROPERTIES_DATA_MULTI, \
    DELETE_GROUP, DELETE_ENTITY
from krules_core.providers import subject_factory
from datetime import datetime
import os
import json

class UpdateGroupColumns(ProcessingFunction):

    def execute(self, subscription, group, current_state):
        subject = subject_factory(f'schema|{subscription}|{group}', use_cache_default=False)
        subject.set("columns", lambda v: sorted(list(set((v or []) + list(current_state.keys())))))
        self.payload["columns"] = subject.get("columns")
        subject.store()



rulesdata: List[Rule] = [
    Rule(
        name="ingestion-multi-receiver",
        subscribe_to=[SUBJECT_PROPERTIES_DATA_MULTI],
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
        subscribe_to=[SUBJECT_PROPERTIES_DATA],
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
                subject_dest="current_state",
                track_last_update=True
            ),
            SetSubjectProperties(
                props=lambda payload: payload["data"],
                unmuted="*"
            ),
            StoreSubject()
        ]
    ),
    Rule(
        name="property-changed-propagation",
        subscribe_to=[SubjectPropertyChanged],
        description=
        """
        Propagate subject property changed event
        """,
        filters=[
            SubjectNameMatch(
                "^entity[|](?P<subscription>.+)[|](?P<group>.+)[|](?P<id>.+)$",
                payload_dest="entity_base_info"
            ),
            OnSubjectPropertyChanged("current_state")
        ],
        processing=[
            UpdateGroupColumns(
                subscription=lambda payload: payload["entity_base_info"]["subscription"],
                group=lambda payload: payload["entity_base_info"]["group"],
                current_state=lambda payload: payload["value"],
            ),
            SetPayloadProperty("changed_properties", lambda payload: [
                            k for k, v in payload["value"].items() if
                            payload["old_value"] is None or k not in payload[
                                "old_value"] or payload["old_value"].get(k) != v
                            ]),
            Route(
                event_type=ENTITY_STATE_CHANGED,
                payload=lambda payload: {
                    "id": payload["entity_base_info"]["id"],
                    "subscription": payload["entity_base_info"]["subscription"],
                    "group": payload["entity_base_info"]["group"],
                    "state": payload["value"],
                    "prev_state": payload["old_value"],
                    "changed_properties": payload["changed_properties"],
                },
                dispatch_policy=DispatchPolicyConst.DIRECT,
                topic=os.environ["STATE_CHANGES_TOPIC"],
                changed_properties= lambda payload: json.dumps(payload["changed_properties"]),
            )
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
        name="on-property-changed-update-event-sourcing",
        subscribe_to=[SubjectPropertyChanged],
        description=
        """
        Store state changes
        """,
        filters=[
            SubjectNameMatch(
                "^entity[|](?P<subscription>.+)[|](?P<group>.+)[|](?P<id>.+)$",
                payload_dest="entity_base_info"
            ),
            OnSubjectPropertyChanged("current_state")
        ],
        processing=[
            WriteDocument(
                collection=lambda payload:
                # f"event_sourcing",
                f"{payload['entity_base_info']['subscription']}/groups/{payload['entity_base_info']['group']}/{payload['entity_base_info']['id']}/event_sourcing",
                data=lambda self: {
                    "datetime": datetime.now().isoformat(),
                    # "subscription": self.payload['entity_base_info']['subscription'],
                    # "group": self.payload['entity_base_info']['group'],
                    "entity_id": self.payload['entity_base_info']['id'],
                    "state": self.subject.get("current_state"),
                    "changed_properties": [
                        k for k, v in self.payload["value"].items() if
                        self.payload["old_value"] is None or k not in self.payload[
                            "old_value"] or self.payload["old_value"].get(k) != v
                    ],
                    "origin_id": self.subject.event_info()["originid"]
                }
            ),
        ]
    ),
    Rule(
        name="delete-group",
        subscribe_to=[DELETE_GROUP],
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
            DeleteCollection(
                collection=lambda payload:
                f"{payload['entity_base_info']['subscription']}/groups/{payload['entity_base_info']['group']}"
            ),
            Process(
                lambda payload: subject_factory(f"schema|{payload['entity_base_info']['subscription']}|{payload['entity_base_info']['group']}").flush()
            ),
            SetPayloadProperty("collection", lambda payload: f"{payload['entity_base_info']['subscription']}/settings/schemas"),
            SetPayloadProperty("document", lambda payload: payload['entity_base_info']['group']),
            DeleteDocument(
                collection=lambda payload: f"{payload['entity_base_info']['subscription']}/settings/schemas",
                document=lambda payload: payload['entity_base_info']['group']
            ),
            FlushSubject()
        ]
    ),
    Rule(
        name="delete-entity",
        subscribe_to=[DELETE_ENTITY],
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
            DeleteDocument(
                collection=lambda payload: f"{payload['entity_base_info']['subscription']}/groups/{payload['entity_base_info']['group']}",
                document=lambda payload: payload['entity_base_info']['id']
            ),
            FlushSubject(),
        ]
    ),
]
