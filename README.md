Prometheus + Grafana for a Dockerized app

This setup gives you app metrics, container metrics (cAdvisor), and host metrics (node-exporter).

Layout
monitoring/
├── docker-compose.yml
├── prometheus/
│   ├── prometheus.yml
│   └── alerts.yml
└── grafana/
    └── provisioning/
        └── datasources/
            └── prometheus.yml

alerts.yml is optional. I have not made it.

Run your application:

echo "GRAFANA_ADMIN_PASSWORD=change-me" > .env
docker compose up -d

Prometheus: http://localhost:9090
Grafana: http://localhost:3000


Dashboards

In Grafana go to Dashboards → New → Import and enter an ID:

1860: Node Exporter Full (host)
14282: cAdvisor / Docker containers
Build your own for app metrics. Useful PromQL:

# Request rate
sum(rate(http_requests_total[5m])) by (path)

# p95 latency
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, path))

# Container memory
container_memory_working_set_bytes{name!=""}

Once you’ve built a good dashboard, export it as JSON and add a dashboards provisioning folder so it’s version-controlled.

Production notes:

Don’t expose 9090/3000 publicly. Put them behind a reverse proxy with TLS and auth, or bind to 127.0.0.1.

Multiple app replicas or dynamic containers: replace static_configs with docker_sd_configs (mount the Docker socket read-only) or Consul/DNS service discovery.

Kubernetes: use kube-prometheus-stack via Helm instead.

Long-term storage / HA: consider Thanos, Mimir, or remote_write to a managed backend.

Avoid high-cardinality labels (user IDs, raw URLs with IDs). They’re the most common cause of Prometheus memory blowups.
