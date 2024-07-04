import pulumi_kubernetes as kubernetes
import pulumi

from krules_dev import sane_utils
from krules_dev.sane_utils import get_stack_reference

#from pulumi_kubernetes import Provider as k8s_provider
import pulumi_gcp as gcp


# Initialize a config object
config = pulumi.Config()

# Get the name of the "parent" stack that we will reference.
app_name = sane_utils.check_env("app_name")
project_name = sane_utils.check_env("project_name")
target = sane_utils.get_target()

ingress_host = sane_utils.check_env("ingress_host")

base_stack_ref = get_stack_reference("base")


def get_static_ip_name():
    ip_name = sane_utils.get_var_for_target("STATIC_IP_NAME")
    if ip_name is None:
        ip_name = f"{project_name}-{target}-ip"
    return ip_name

gcp_provider = gcp.Provider("gcp-provider", project=sane_utils.get_project_id())

# Create the ManagedCertificate
# managed_cert = gcp.compute.ManagedSslCertificate(
#     f"{project_name}-{target}-backend-ingress",
#     name=sane_utils.name_resource("backend-ingress"),
#     managed=gcp.compute.ManagedSslCertificateManagedArgs(
#         domains=[ingress_host],
#     ),
#     opts=pulumi.ResourceOptions(provider=gcp_provider),
# )

# # use managed_cert.name in the Ingress annotations
#managed_certificate_name = managed_cert.name

ingress = kubernetes.networking.v1.Ingress(
    f"{project_name}-{target}-ingress",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        annotations={
            "kubernetes.io/ingress.class": "gce",
            "kubernetes.io/ingress.global-static-ip-name": get_static_ip_name(),
            # "networking.gke.io/v1beta1.FrontendConfig": f"{project_name}-{target}-fe-https",
            #"networking.gke.io/managed-certificates": managed_certificate_name,
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
                        kubernetes.networking.v1.HTTPIngressPathArgs(
                            path="/api/subscriptions/v1/*",
                            path_type="ImplementationSpecific",
                            backend=kubernetes.networking.v1.IngressBackendArgs(
                                service=kubernetes.networking.v1.IngressServiceBackendArgs(
                                    name="firebase-authadmin",
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

be_https_policy = kubernetes.apiextensions.CustomResource(
    f"{project_name}-{target}-backend-https",
    api_version="networking.gke.io/v1beta1",
    kind="FrontendConfig",
    metadata={
        "name": f"{project_name}-{target}-backend-https",
    },
    spec={
        "sslPolicy": "gke-ingress-ssl-policy-https",
        "redirectToHttps": {
            "enabled": True
        }
    },
)
