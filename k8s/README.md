# Kubernetes manifests

Estos manifiestos son un baseline para el bonus del proyecto.

El pipeline CI/CD los aplica automaticamente en la etapa `deploy-kubernetes` al hacer push a `main` (o ejecucion manual).

## Aplicar en orden

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/todo-api-configmap.yaml
kubectl apply -f k8s/todo-api-pvc.yaml
kubectl apply -f k8s/todo-api-deployment.yaml
kubectl apply -f k8s/todo-api-service.yaml
kubectl apply -f k8s/prometheus-configmap.yaml
kubectl apply -f k8s/prometheus-deployment.yaml
kubectl apply -f k8s/prometheus-service.yaml
kubectl apply -f k8s/grafana-secret.yaml
kubectl apply -f k8s/grafana-pvc.yaml
kubectl apply -f k8s/grafana-datasource-configmap.yaml
kubectl apply -f k8s/grafana-deployment.yaml
kubectl apply -f k8s/grafana-service.yaml
```

## Ajustes obligatorios antes de produccion

- Reemplazar `nexus.example.com:8083/todo-api:latest` por imagen real de Nexus
- Crear secreto de pull para el registry privado de Nexus:

```bash
kubectl create secret docker-registry nexus-regcred \
	--docker-server=<nexus-host:8083> \
	--docker-username=<usuario> \
	--docker-password=<password> \
	--namespace devops-final
```

- Cambiar password en `grafana-secret.yaml`
- Definir almacenamiento persistente real (StorageClass/PV)
- Definir Ingress + TLS
