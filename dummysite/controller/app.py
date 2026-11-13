from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException

GROUP = "stable.dwk"
VERSION = "v1"
PLURAL = "dummysites"


def owner(obj):
    return [client.V1OwnerReference(
        api_version=f"{GROUP}/{VERSION}",
        kind="DummySite",
        name=obj["metadata"]["name"],
        uid=obj["metadata"]["uid"],
        controller=True,
        block_owner_deletion=True,
    )]


def create_site(apps, core, obj):
    name = f"dummysite-{obj['metadata']['name']}"
    namespace = obj["metadata"]["namespace"]
    url = obj["spec"]["website_url"]
    labels = {"app": name}

    # The init container downloads the page, nginx serves it.
    deployment = client.V1Deployment(
        metadata=client.V1ObjectMeta(name=name, namespace=namespace, owner_references=owner(obj)),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector=client.V1LabelSelector(match_labels=labels),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels=labels),
                spec=client.V1PodSpec(
                    init_containers=[client.V1Container(
                        name="download",
                        image="curlimages/curl:8.11.1",
                        command=["curl", "-sSL", "-A", "Mozilla/5.0", "-o", "/site/index.html", url],
                        volume_mounts=[client.V1VolumeMount(name="site", mount_path="/site")],
                    )],
                    containers=[client.V1Container(
                        name="nginx",
                        image="nginx:1.27-alpine",
                        ports=[client.V1ContainerPort(container_port=80)],
                        volume_mounts=[client.V1VolumeMount(name="site", mount_path="/usr/share/nginx/html")],
                    )],
                    volumes=[client.V1Volume(name="site", empty_dir=client.V1EmptyDirVolumeSource())],
                ),
            ),
        ),
    )
    service = client.V1Service(
        metadata=client.V1ObjectMeta(name=name, namespace=namespace, owner_references=owner(obj)),
        spec=client.V1ServiceSpec(
            selector=labels,
            ports=[client.V1ServicePort(port=80, target_port=80)],
        ),
    )
    for create in (lambda: apps.create_namespaced_deployment(namespace, deployment),
                   lambda: core.create_namespaced_service(namespace, service)):
        try:
            create()
        except ApiException as e:
            if e.status != 409:
                raise
    print(f"DummySite {namespace}/{obj['metadata']['name']}: serving {url} with service {name}", flush=True)


def main():
    config.load_incluster_config()
    custom = client.CustomObjectsApi()
    apps = client.AppsV1Api()
    core = client.CoreV1Api()
    while True:
        try:
            for event in watch.Watch().stream(custom.list_cluster_custom_object, GROUP, VERSION, PLURAL):
                if event["type"] == "ADDED":
                    create_site(apps, core, event["object"])
        except Exception as e:
            print(f"watch error: {e}", flush=True)


if __name__ == "__main__":
    main()
