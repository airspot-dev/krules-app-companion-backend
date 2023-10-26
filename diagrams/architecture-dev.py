from diagrams import Cluster, Diagram
from diagrams.gcp.database import Memorystore, SQL, Firestore
from diagrams.gcp.security import Iam
from diagrams.gcp.compute import Run
from diagrams.gcp.analytics import PubSub
from diagrams.k8s.compute import Deployment
from diagrams.k8s.rbac import SA

graph_attr = {
    #"splines": "spline",
    "layout": "fdp",
    }
with Diagram("Companion Architecture (dev current)", graph_attr=graph_attr):
    with Cluster("Host Project (krules-dev-254113)"):
        redis = Memorystore("redis")
        cloudsql = SQL("postgresql")

        with Cluster("K8S - namespace") as k8s_ns:
            gke_sa_default = SA("default")
            celery_worker = Deployment("celery-worker")
            ingestion_receiver = Deployment("ingestion-receiver")


    with Cluster("Service Project (airspot-krules-companion-dev"):
        sa_default = Iam("default")
        firestore = Firestore("state+eventsource")
        backend_api = Run("backend-api")
        pubsub_ingestion = PubSub("ingestion")

    gke_sa_default >> sa_default

    celery_worker >> redis
    celery_worker >> cloudsql

    backend_api >> redis
    backend_api >> cloudsql
    backend_api >> pubsub_ingestion

    backend_api >> firestore

    pubsub_ingestion >> ingestion_receiver
    ingestion_receiver >> firestore
