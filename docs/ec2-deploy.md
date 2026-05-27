# Guia de despliegue EC2 (Nexus en Docker + servicios en Kubernetes)

Este proyecto usa un esquema hibrido en EC2:

- Nexus corre como contenedor Docker (fuera de Kubernetes).
- API, Prometheus y Grafana corren en Kubernetes (k3s) usando los manifiestos de k8s/.

## 1. Preparar la instancia EC2

- SO recomendado: Ubuntu 22.04.
- Tipo de instancia sugerido para laboratorio: t3.medium o superior.
- Security Group minimo:
  - 22/tcp para SSH
  - 8081/tcp para UI/API de Nexus
  - 8083/tcp para Docker Registry de Nexus
  - 80/tcp para trafico HTTP de Ingress (Traefik en k3s)
  - 32000/tcp para acceso externo a Grafana (Service NodePort actual)
  - 6443/tcp solo si GitHub Actions va a conectarse al API de Kubernetes desde internet

Notas de puertos Kubernetes en este repo:

- Grafana se expone por NodePort 32000 (k8s/grafana-service.yaml).
- Todo API y Prometheus estan como ClusterIP, por lo que no requieren puertos extra en el Security Group mientras sigan asi.
- Si cambias Grafana a Ingress, podrias cerrar 32000 y usar solo 80/443.

## 2. Instalar prerequisitos

```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin curl
sudo usermod -aG docker $USER
newgrp docker
```

## 3. Clonar el repositorio

```bash
git clone <repo-url>
cd devops-final-seed
```

## 4. Levantar solo Nexus con Docker

El archivo docker-compose.yml define varios servicios, pero en EC2 se debe iniciar solo Nexus.

```bash
docker compose up -d nexus
docker compose ps
```

Validar:

- http://<ec2-public-dns-o-ip>:8081
- http://<ec2-public-dns-o-ip>:8083/v2/

## 5. Configuracion inicial de Nexus

En la UI de Nexus:

- Crear repositorio docker hosted para imagenes (conector HTTP en 8083).
- Crear repositorio raw llamado devops-raw para reportes de pipeline.
- Crear usuario de CI con permisos de push/pull sobre ambos repositorios.

## 6. Instalar k3s en la misma EC2

```bash
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server --write-kubeconfig-mode 644 --tls-san <ec2-public-dns-o-ip>" sh -
sudo kubectl get nodes
```

Si quieres usar kubectl sin sudo:

```bash
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER:$USER ~/.kube/config
```

## 7. Permitir pulls desde Nexus HTTP en k3s

Si el registry de Nexus esta en HTTP (sin TLS), crea este archivo:

```bash
sudo mkdir -p /etc/rancher/k3s
sudo tee /etc/rancher/k3s/registries.yaml > /dev/null <<'EOF'
mirrors:
  "<ec2-public-dns-o-ip>:8083":
    endpoint:
      - "http://<ec2-public-dns-o-ip>:8083"

configs:
  "<ec2-public-dns-o-ip>:8083":
    auth:
      username: "<nexus-user>"
      password: "<nexus-password>"
EOF
sudo systemctl restart k3s
```

## 8. Configurar variables y secretos en GitHub

Variables de repositorio:

- NEXUS_REGISTRY=<ec2-public-dns-o-ip>:8083
- NEXUS_DOCKER_IMAGE=<ec2-public-dns-o-ip>:8083/todo-api
- NEXUS_RAW_URL=http://<ec2-public-dns-o-ip>:8081/repository/devops-raw

Secrets de repositorio:

- NEXUS_USERNAME=<usuario-ci>
- NEXUS_PASSWORD=<password-ci>
- KUBE_CONFIG_B64=<contenido base64 del kubeconfig>

Generar KUBE_CONFIG_B64 desde EC2:

```bash
cp /etc/rancher/k3s/k3s.yaml ./kubeconfig-ci.yaml
sed -i "s/127.0.0.1/<ec2-public-dns-o-ip>/g" ./kubeconfig-ci.yaml
base64 -w 0 ./kubeconfig-ci.yaml
```

## 9. Como se dispara el pipeline en este repo

Segun .github/workflows/ci-cd.yml:

- En pull request a dev o main: solo corre quality-security-tests.
- En push a dev: corre quality-security-tests.
- En push a main: corre quality-security-tests, verify-docker, verify-kubernetes, build-and-push-image y deploy-kubernetes.

Nota: actualmente no hay workflow_dispatch en el pipeline.

## 10. Despliegue Kubernetes y validaciones

Al hacer merge/push a main, el job deploy-kubernetes aplica manifiestos y actualiza la imagen del deployment todo-api.

Validar estado:

```bash
kubectl -n devops-final get pods
kubectl -n devops-final get svc
kubectl -n devops-final rollout status deployment/todo-api
```

Probar API:

```bash
curl http://<ec2-public-dns-o-ip>/health
```

## 11. Importante sobre Ingress

Existe el archivo k8s/todo-api-ingress.yaml, pero el job deploy-kubernetes actual no lo aplica en la etapa Apply Kubernetes manifests.

Si necesitas exponer la API por host/path via Traefik, aplicalo manualmente o agrega ese archivo al workflow:

```bash
kubectl apply -f k8s/todo-api-ingress.yaml
```

## 12. Endurecimiento recomendado

- Migrar el registry de Nexus a HTTPS con certificado valido.
- Restringir 8081, 8083 y 6443 por IP o VPN.
- Evitar credenciales estaticas y mover secretos a AWS SSM o Secrets Manager.
- Respaldar /nexus-data y los volumenes persistentes de k3s.
