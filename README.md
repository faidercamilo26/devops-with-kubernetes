# DevOps with Kubernetes 2026

## Exercises

### Chapter 2

- [1.1](https://github.com/faidercamilo26/devops-with-kubernetes/tree/1.1/log-output)
- [1.2](https://github.com/faidercamilo26/devops-with-kubernetes/tree/1.2/todo-app)
- [1.3](https://github.com/faidercamilo26/devops-with-kubernetes/tree/1.3/log-output)
- [1.4](https://github.com/faidercamilo26/devops-with-kubernetes/tree/1.4/todo-app)
- [1.5](https://github.com/faidercamilo26/devops-with-kubernetes/tree/1.5/todo-app)
- [1.6](https://github.com/faidercamilo26/devops-with-kubernetes/tree/1.6/todo-app)
- [1.7](https://github.com/faidercamilo26/devops-with-kubernetes/tree/1.7/log-output)
- [1.8](https://github.com/faidercamilo26/devops-with-kubernetes/tree/1.8/todo-app)
- [1.9](https://github.com/faidercamilo26/devops-with-kubernetes/tree/1.9/ping-pong)
- [1.10](https://github.com/faidercamilo26/devops-with-kubernetes/tree/1.10/log-output)
- [1.11](https://github.com/faidercamilo26/devops-with-kubernetes/tree/1.11/log-output)
- [1.12](https://github.com/faidercamilo26/devops-with-kubernetes/tree/1.12/todo-app)
- [1.13](https://github.com/faidercamilo26/devops-with-kubernetes/tree/1.13/todo-app)

### Chapter 3

- [2.1](https://github.com/faidercamilo26/devops-with-kubernetes/tree/2.1/log-output)
- [2.2](https://github.com/faidercamilo26/devops-with-kubernetes/tree/2.2/todo-backend)
- [2.3](https://github.com/faidercamilo26/devops-with-kubernetes/tree/2.3/log-output)
- [2.4](https://github.com/faidercamilo26/devops-with-kubernetes/tree/2.4/todo-app)
- [2.5](https://github.com/faidercamilo26/devops-with-kubernetes/tree/2.5/log-output)
- [2.6](https://github.com/faidercamilo26/devops-with-kubernetes/tree/2.6/todo-app)
- [2.7](https://github.com/faidercamilo26/devops-with-kubernetes/tree/2.7/ping-pong)
- [2.8](https://github.com/faidercamilo26/devops-with-kubernetes/tree/2.8/todo-backend)
- [2.9](https://github.com/faidercamilo26/devops-with-kubernetes/tree/2.9/todo-cronjob)
- [2.10](https://github.com/faidercamilo26/devops-with-kubernetes/tree/2.10/todo-backend)

### Chapter 4

- [3.1](https://github.com/faidercamilo26/devops-with-kubernetes/tree/3.1/ping-pong)
- [3.2](https://github.com/faidercamilo26/devops-with-kubernetes/tree/3.2/log-output)
- [3.3](https://github.com/faidercamilo26/devops-with-kubernetes/tree/3.3/log-output)
- [3.4](https://github.com/faidercamilo26/devops-with-kubernetes/tree/3.4/ping-pong)
- [3.5](https://github.com/faidercamilo26/devops-with-kubernetes/tree/3.5)
- [3.6](https://github.com/faidercamilo26/devops-with-kubernetes/tree/3.6)
- [3.7](https://github.com/faidercamilo26/devops-with-kubernetes/tree/3.7)
- [3.8](https://github.com/faidercamilo26/devops-with-kubernetes/tree/3.8)
- [3.9](https://github.com/faidercamilo26/devops-with-kubernetes/tree/3.9)
- [3.10](https://github.com/faidercamilo26/devops-with-kubernetes/tree/3.10/todo-backup)
- [3.11](https://github.com/faidercamilo26/devops-with-kubernetes/tree/3.11)
- [3.12](https://github.com/faidercamilo26/devops-with-kubernetes/tree/3.12/screenshots)

### Chapter 5

- [4.1](https://github.com/faidercamilo26/devops-with-kubernetes/tree/4.1/ping-pong)
- [4.2](https://github.com/faidercamilo26/devops-with-kubernetes/tree/4.2/todo-app)
- [4.3](https://github.com/faidercamilo26/devops-with-kubernetes/tree/4.3)
- [4.4](https://github.com/faidercamilo26/devops-with-kubernetes/tree/4.4/ping-pong)

## 3.9 DBaaS vs DIY

Comparison between a Database as a Service (for example Google Cloud SQL for PostgreSQL) and running
Postgres ourselves (a StatefulSet with its own Postgres image and PersistentVolumeClaims, where the
cluster provisions the PersistentVolumes).

### Initialization: work and cost

| | DBaaS (Cloud SQL) | DIY (StatefulSet + PVC) |
|---|---|---|
| Work to start | Create an instance from the console or `gcloud`, create the database and user, and decide how pods reach it (private IP or the Cloud SQL Auth Proxy sidecar). Little work, but it is cloud specific. | Write a Service and a StatefulSet with a `volumeClaimTemplates`, plus a Secret for the password. A few manifests we already know, and they run on any Kubernetes cluster. |
| Cost | Pay for the instance (vCPU and memory) for every hour it exists, plus storage, backups and network, even when idle. A high availability instance roughly doubles it. | Pay only for the persistent disk and for the node resources the pod uses. No extra charge for the database itself, so it is much cheaper for a small project. |
| Portability | Tied to the provider and to its connection method. | The same manifests work on a local cluster, GKE or any other cluster. |

### Maintenance

- **DBaaS:** the provider applies operating system and Postgres minor updates in a maintenance window, monitors the
  instance, and offers high availability (automatic failover to a standby) and read replicas as options. We only
  tune settings and size.
- **DIY:** we are responsible for everything. We choose and upgrade the image, plan major version upgrades,
  watch disk usage and resize the volume, handle crashes and failover (a single replica means downtime while the
  pod restarts), and set up replication ourselves if we need it.

### Backups: methods and how easy they are to use

- **DBaaS:** automated daily backups and point in time recovery are built in and need almost no setup. A restore is a
  button or one command, and it can create a new instance from any recent point. On-demand backups and exports to
  object storage are also available. The cost is that retention and storage are billed.
- **DIY:** nothing is backed up by default, and a persistent volume is not a backup because losing the volume loses
  the data. We must build it: a CronJob running `pg_dump` and storing the file somewhere safe (as in exercise
  3.10), and/or volume snapshots of the disk. It is flexible and cheap, but restoring means us loading the dump
  into a fresh database by hand, and point in time recovery needs extra tooling (WAL archiving). We also have to
  test the restore, because an untested backup may not work.

### Conclusion

For a production system where losing data or being down is costly, a DBaaS is usually worth the price because backups,
updates and failover are solved. For a small project, a learning environment or when cost and portability matter more,
running Postgres in a StatefulSet is simpler and cheaper, as long as we accept owning the backups and the maintenance.

## 4.3 Prometheus

Prometheus is reached through its Service:

```
kubectl port-forward svc/prom-prometheus-server -n monitoring 9090:80
```

Query that shows the number of pods created by StatefulSets in the monitoring namespace
(open http://localhost:9090 and run it in the Graph tab):

```
count(kube_pod_info{namespace="monitoring", created_by_kind="StatefulSet"})
```

In this cluster it returns `1`: the only pod created by a StatefulSet in `monitoring` is `loki-0`.
`kube_pod_info` has one series per pod, `namespace` selects the monitoring stack and `created_by_kind`
is the kind of controller that created the pod.
