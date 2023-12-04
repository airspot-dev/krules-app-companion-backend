import pulumi_kubernetes as kubernetes
from pulumi import Config

from krules_dev import sane_utils
from krules_dev.sane_utils import get_stack_reference

# Initialize a config object
config = Config()

# Get the name of the "parent" stack that we will reference.
app_name = sane_utils.check_env("app_name")
project_name = sane_utils.check_env("project_name")
target = sane_utils.get_target()

ingress_host = sane_utils.check_env("ingress_host")

base_stack_ref = get_stack_reference("base")

ingress = kubernetes.networking.v1.Ingress(
    f"{project_name}-{target}-ingress",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        annotations={
            "kubernetes.io/ingress.class": "gce",
            "kubernetes.io/ingress.global-static-ip-name": f"{project_name}-{target}-ip",
            "networking.gke.io/managed-certificates": f"{project_name}-{target}-cert",
            #"networking.gke.io/v1beta1.FrontendConfig": f"{project_name}-{target}-fe-https",
        }
    ),
    spec=kubernetes.networking.v1.IngressSpecArgs(
        rules=[
            kubernetes.networking.v1.IngressRuleArgs(
                host=ingress_host,
                http=kubernetes.networking.v1.HTTPIngressRuleValueArgs(
                    paths=[
                        kubernetes.networking.v1.HTTPIngressPathArgs(
                            path="/*",
                            path_type="ImplementationSpecific",
                            backend=kubernetes.networking.v1.IngressBackendArgs(
                                service=kubernetes.networking.v1.IngressServiceBackendArgs(
                                    name="frontend",
                                    port=kubernetes.networking.v1.ServiceBackendPortArgs(
                                        number=80,
                                    )
                                )
                            )
                        ),
                        kubernetes.networking.v1.HTTPIngressPathArgs(
                            path="/api/v1/*",
                            path_type="ImplementationSpecific",
                            backend=kubernetes.networking.v1.IngressBackendArgs(
                                service=kubernetes.networking.v1.IngressServiceBackendArgs(
                                    name="backend-api",
                                    port=kubernetes.networking.v1.ServiceBackendPortArgs(
                                        number=80,
                                    )
                                )
                            )
                        ),
                        kubernetes.networking.v1.HTTPIngressPathArgs(
                            path="/api/scheduler/v1/*",
                            path_type="ImplementationSpecific",
                            backend=kubernetes.networking.v1.IngressBackendArgs(
                                service=kubernetes.networking.v1.IngressServiceBackendArgs(
                                    name="backend-api",
                                    port=kubernetes.networking.v1.ServiceBackendPortArgs(
                                        number=80,
                                    )
                                )
                            )
                        ),
                    ]
                )
            )
        ]
    )
)

managed_certificate = kubernetes.apiextensions.CustomResource(
    f"{project_name}-{target}-cert",
    api_version="networking.gke.io/v1",
    kind="ManagedCertificate",
    metadata={
        "name": f"{project_name}-{target}-cert",
    },
    spec={
        "domains": [
            ingress_host,
        ],
    },
)

# fe_https_policy = kubernetes.apiextensions.CustomResource(
#     f"{project_name}-{target}-fe-https",
#     api_version="networking.gke.io/v1beta1",
#     kind="FrontendConfig",
#     metadata={
#         "name": f"{project_name}-{target}-fe-https",
#     },
#     spec={
#         "sslPolicy": "gke-ingress-ssl-policy-https",
#         "redirectToHttps": {
#             "enabled": True
#         }
#     },
# )
