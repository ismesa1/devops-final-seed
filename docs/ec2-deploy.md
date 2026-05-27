# Guia de despliegue en EC2

Este repositorio queda listo para desplegar con Kubernetes (k3s) en EC2 y usando Nexus como repositorio de artefactos.

## 1. Preparar EC2

- Crear instancia Ubuntu 22.04 o Amazon Linux 2023
- Abrir puertos en Security Group:
  - `22` (SSH)
  - `8081` (Nexus UI/API)
  - `8083` (Nexus Docker Registry)
  - `30000-32767` (NodePort de Kubernetes, si se requieren servicios externos)
  - `6443` (Kubernetes API, solo si el job deploy corre en `ubuntu-latest`)
- Instalar Docker y plugin de Compose

## 2. Obtener codigo

```bash
git clone <repo-url>
cd devops-final-seed
```

## 3. Levantar Nexus en EC2

`docker-compose.yml` se sigue usando para Nexus. La orquestacion de app/observabilidad pasa a Kubernetes.

```bash
docker compose up -d nexus
```

## 4. Configurar Nexus (primera vez)

- Entrar a `http://<ec2-public-ip-or-dns>:8081`
- Crear repositorio `docker-hosted` con conector HTTP en puerto `8083`
- Crear repositorio `devops-raw` para almacenar reportes de pipeline
- Crear usuario de CI con permisos de push/pull

## 5. Instalar Kubernetes (k3s)

```bash
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server --write-kubeconfig-mode 644 --tls-san <ec2-public-ip-or-dns>" sh -
kubectl get nodes
```

## 6. Configurar k3s para pull desde Nexus HTTP (si aplica)

Si Nexus esta en `http://<host>:8083` sin TLS, crea `/etc/rancher/k3s/registries.yaml`:

```yaml
mirrors:
  "<ec2-public-ip-or-dns>:8083":
    endpoint:
      - "http://<ec2-public-ip-or-dns>:8083"

configs:
  "<ec2-public-ip-or-dns>:8083":
    auth:
      username: "<nexus-user>"
      password: "<nexus-password>"
```

Luego reinicia k3s:

```bash
sudo systemctl restart k3s
```

## 7. Configurar CI/CD para deploy Kubernetes

El workflow ahora despliega en Kubernetes (`deploy-kubernetes`) despues del build de imagen.

Configurar variables en GitHub:

- `NEXUS_REGISTRY=<ec2-public-ip-or-dns>:8083`
- `NEXUS_DOCKER_IMAGE=<ec2-public-ip-or-dns>:8083/todo-api`
- `NEXUS_RAW_URL=http://<ec2-public-ip-or-dns>:8081/repository/devops-raw`

Configurar secrets en GitHub:

- `NEXUS_USERNAME=<usuario-ci>`
- `NEXUS_PASSWORD=<password-ci>`
- `KUBE_CONFIG_B64=<kubeconfig base64>`

Para generar `KUBE_CONFIG_B64` en EC2:

```bash
cp /etc/rancher/k3s/k3s.yaml ./kubeconfig-ci.yaml
sed -i "s/127.0.0.1/<ec2-public-ip-or-dns>/g" ./kubeconfig-ci.yaml
base64 -w 0 ./kubeconfig-ci.yaml
```

## 8. Despliegue

- Hacer push/merge a `main` para disparar deploy automatico en Kubernetes
- O ejecutar manualmente con `workflow_dispatch`

## 9. Validar despliegue

```bash
kubectl -n devops-final get pods
kubectl -n devops-final get svc
kubectl -n devops-final rollout status deployment/todo-api
```

Nexus se valida en:

- `http://<ec2-public-ip-or-dns>:8081`

## 10. Endurecimiento recomendado

- Usar TLS para Nexus Docker Registry (evitar HTTP en 8083)
- Restringir puertos `8081`, `8083` y `6443` por IP/VPN
- Rotar credenciales y mover secretos a AWS SSM/Secrets Manager
- Programar backups de `/nexus-data` y de volumenes del cluster
