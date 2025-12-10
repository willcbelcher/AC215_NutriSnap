import pulumi
from pulumi_gcp import container, artifactregistry, compute
from pulumi_kubernetes import Provider, core, apps, meta
import pulumi_kubernetes as k8s

# Config
config = pulumi.Config()
gcp_config = pulumi.Config("gcp")
project = gcp_config.require("project")
region = gcp_config.get("region", "us-central1")
zone = gcp_config.get("zone", "us-central1-a")

# 0. Network
network = compute.Network("nutrisnap-network",
    auto_create_subnetworks=False,
    description="VPC for NutriSnap"
)

subnet = compute.Subnetwork("nutrisnap-subnet",
    ip_cidr_range="10.0.0.0/16",
    network=network.id,
    region=region
)

# 1. GKE Cluster
cluster = container.Cluster("nutrisnap-cluster",
    initial_node_count=1,
    min_master_version="latest",
    node_version="latest",
    network=network.name,
    subnetwork=subnet.name,
    node_config=container.ClusterNodeConfigArgs(
        machine_type="e2-standard-4", # Need some RAM for the model
        oauth_scopes=[
            "https://www.googleapis.com/auth/cloud-platform",
        ],
    ),
    location=zone,
    deletion_protection=False,
)

import subprocess

def get_access_token():
    try:
        return subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True).strip()
    except Exception:
        return ""

access_token = get_access_token()

# Export Kubeconfig
kubeconfig = pulumi.Output.all(cluster.name, cluster.endpoint, cluster.master_auth).apply(
    lambda args: """apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: {2}
    server: https://{1}
  name: {0}
contexts:
- context:
    cluster: {0}
    user: {0}
  name: {0}
current-context: {0}
kind: Config
preferences: {{}}
users:
- name: {0}
  user:
    token: {3}
""".format(args[0], args[1], args[2]['cluster_ca_certificate'], access_token)
)

# K8s Provider
k8s_provider = Provider("k8s-provider", kubeconfig=kubeconfig)

# Namespace
ns = core.v1.Namespace("nutrisnap-ns",
    metadata=meta.v1.ObjectMetaArgs(name="nutrisnap"),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# 2. Postgres
postgres_labels = {"app": "postgres"}
postgres_deploy = apps.v1.Deployment("postgres-deploy",
    metadata=meta.v1.ObjectMetaArgs(namespace=ns.metadata.name),
    spec=apps.v1.DeploymentSpecArgs(
        selector=meta.v1.LabelSelectorArgs(match_labels=postgres_labels),
        replicas=1,
        template=core.v1.PodTemplateSpecArgs(
            metadata=meta.v1.ObjectMetaArgs(labels=postgres_labels),
            spec=core.v1.PodSpecArgs(
                containers=[core.v1.ContainerArgs(
                    name="postgres",
                    image="postgres:15",
                    env=[
                        core.v1.EnvVarArgs(name="POSTGRES_USER", value="user"),
                        core.v1.EnvVarArgs(name="POSTGRES_PASSWORD", value="password"),
                        core.v1.EnvVarArgs(name="POSTGRES_DB", value="nutrisnap"),
                    ],
                    ports=[core.v1.ContainerPortArgs(container_port=5432)],
                )],
            ),
        ),
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

postgres_svc = core.v1.Service("postgres-svc",
    metadata=meta.v1.ObjectMetaArgs(namespace=ns.metadata.name, name="postgres"),
    spec=core.v1.ServiceSpecArgs(
        selector=postgres_labels,
        ports=[core.v1.ServicePortArgs(port=5432)],
        type="ClusterIP",
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# 4. Backend
backend_labels = {"app": "nutrisnap-backend"}
backend_deploy = apps.v1.Deployment("backend-deploy",
    metadata=meta.v1.ObjectMetaArgs(namespace=ns.metadata.name),
    spec=apps.v1.DeploymentSpecArgs(
        selector=meta.v1.LabelSelectorArgs(match_labels=backend_labels),
        replicas=1,
        template=core.v1.PodTemplateSpecArgs(
            metadata=meta.v1.ObjectMetaArgs(labels=backend_labels),
            spec=core.v1.PodSpecArgs(
                containers=[core.v1.ContainerArgs(
                    name="backend",
                    image=f"us-east4-docker.pkg.dev/{project}/nutrisnap-containers/nutrisnap-backend:latest",
                    ports=[core.v1.ContainerPortArgs(container_port=8000)],
                    env=[
                        core.v1.EnvVarArgs(name="DATABASE_URL", value="postgresql://user:password@postgres:5432/nutrisnap"),
                        # Vertex AI Configuration
                        core.v1.EnvVarArgs(name="VERTEX_ENDPOINT_ID", value="projects/429605625307/locations/us-central1/endpoints/8271624876247220224"),
                        core.v1.EnvVarArgs(name="VERTEX_PROJECT_ID", value="nutrisnap-473915"),
                        core.v1.EnvVarArgs(name="VERTEX_REGION", value="us-central1"),
                        core.v1.EnvVarArgs(name="GCP_PROJECT", value=project),
                        core.v1.EnvVarArgs(name="GCP_LOCATION", value=region),
                    ],
                )],
            ),
        ),
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

backend_svc = core.v1.Service("backend-svc",
    metadata=meta.v1.ObjectMetaArgs(namespace=ns.metadata.name, name="backend-service"),
    spec=core.v1.ServiceSpecArgs(
        selector=backend_labels,
        ports=[core.v1.ServicePortArgs(port=80, target_port=8000)],
        type="LoadBalancer", # Expose for testing/frontend
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# 5. Frontend
frontend_labels = {"app": "nutrisnap-frontend"}
frontend_deploy = apps.v1.Deployment("frontend-deploy",
    metadata=meta.v1.ObjectMetaArgs(namespace=ns.metadata.name),
    spec=apps.v1.DeploymentSpecArgs(
        selector=meta.v1.LabelSelectorArgs(match_labels=frontend_labels),
        replicas=1,
        template=core.v1.PodTemplateSpecArgs(
            metadata=meta.v1.ObjectMetaArgs(labels=frontend_labels),
            spec=core.v1.PodSpecArgs(
                containers=[core.v1.ContainerArgs(
                    name="frontend",
                    image=f"us-east4-docker.pkg.dev/{project}/nutrisnap-containers/nutrisnap-frontend:latest",
                    ports=[core.v1.ContainerPortArgs(container_port=3000)],
                    env=[
                        # Internal URL for Server-Side Rendering (SSR)
                        core.v1.EnvVarArgs(name="NUXT_API_BASE", value="http://backend-service"),
                        
                        # Public URL for Client-Side Rendering (CSR)
                        core.v1.EnvVarArgs(
                            name="NUXT_PUBLIC_API_BASE", 
                            value=backend_svc.status.apply(lambda s: f"http://{s.load_balancer.ingress[0].ip}" if s.load_balancer.ingress else "http://localhost:8000")
                        ),
                    ],
                )],
            ),
        ),
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

frontend_svc = core.v1.Service("frontend-svc",
    metadata=meta.v1.ObjectMetaArgs(namespace=ns.metadata.name, name="frontend-service"),
    spec=core.v1.ServiceSpecArgs(
        selector=frontend_labels,
        ports=[core.v1.ServicePortArgs(port=80, target_port=3000)],
        type="LoadBalancer",
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Exports
pulumi.export("kubeconfig", kubeconfig)
pulumi.export("backend_ip", backend_svc.status.apply(lambda s: s.load_balancer.ingress[0].ip if s.load_balancer.ingress else "pending"))
pulumi.export("frontend_ip", frontend_svc.status.apply(lambda s: s.load_balancer.ingress[0].ip if s.load_balancer.ingress else "pending"))
