from . import gke_sa_default, vpcaccess_connector_project_id
import pulumi
import pulumi_gcp as gcp

# network = gcp.compute.Network(
#     vpcaccess_network,
#     auto_create_subnetworks=False,
#     project=vpcaccess_project_id
# )
#
# # subnetwork = gcp.compute.Subnetwork(
# #     vpcaccess_subnetwork,
# #     ip_cidr_range=vpcaccess_ip_cidr_range,
# #     region=vpcaccess_region,
# #     network=vpcaccess_network,
# #     project=vpcaccess_project_id
# # )
#
# connector = gcp.vpcaccess.Connector(
#     f"{project_name}-{target}",
#     # subnet=gcp.vpcaccess.ConnectorSubnetArgs(
#     #     name=vpcaccess_subnetwork,
#     # ),
#     network=vpcaccess_network,
#     project=vpcaccess_project_id,
#     region=vpcaccess_region,
#     ip_cidr_range=vpcaccess_ip_cidr_range,
#     # machine_type="e2-standard-4"
# )
#
# pulumi.export("connector", connector)
#
#
# if vpcaccess_project_id == project_id:
#
#     vpcaccess_connector_user_iam_binding = gcp.serviceaccount.IAMBinding(
#         "vpcaccess_connector_user_iam_binding",
#         service_account_id=gke_sa_default.account_id,
#         role="roles/vpcaccess.user",
#     )


vpcaccess_connector_user_iam_member = gcp.projects.IAMMember(
    'vpcaccess_connector_user_iam_member',
    member=gke_sa_default.email.apply(lambda email: f"serviceAccount:{email}"),
    project=vpcaccess_connector_project_id,
    role="roles/vpcaccess.user"
    # role="roles/compute.networkUser"
)

pulumi.export('vpcaccess_connector_user_iam_member', vpcaccess_connector_user_iam_member)
