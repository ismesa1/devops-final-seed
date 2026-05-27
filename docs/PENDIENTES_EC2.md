# Pendientes para cerrar en AWS EC2

Este archivo resume lo que falta completar manualmente fuera del alcance del repositorio.

## 1. Infraestructura AWS

- Crear instancia EC2 productiva (tipo, disco, red)
- Configurar Security Group con minimo privilegio
- Definir Elastic IP o DNS estable
- Configurar backups/snapshots para volumenes

## 2. Acceso a imagen privada Nexus

- Crear usuario de CI/CD en Nexus con permisos de push/pull
- Autenticar Docker en EC2 (`docker login <nexus-host>:8083`)
- Configurar rotacion de credenciales en Nexus
- Verificar que existan repositorios `docker-hosted` y `devops-raw`

## 3. Secretos y configuracion sensible

- Mover credenciales de Grafana a AWS SSM Parameter Store o Secrets Manager
- Gestionar secretos sin exponerlos en `.env`
- Definir politica de rotacion de secretos

## 4. Exposicion segura de servicios

- Configurar reverse proxy (Nginx/Traefik) o ALB
- Habilitar HTTPS con certificado valido
- Restringir Prometheus y Grafana por IP/VPN

## 5. Operacion y continuidad

- Definir estrategia de despliegue (manual, script, o CD remoto)
- Definir monitoreo de host EC2 (CPU, RAM, disco)
- Definir alertas (ej. Alertmanager + email/Slack)
- Definir procedimiento de rollback

## 6. Kubernetes (si se activa este camino)

- Elegir distribucion (k3s en EC2 o EKS)
- Configurar storage class para PVC
- Ajustar manifiestos con imagen real y secretos
- Definir ingress controller y certificados
- Definir exposicion segura del API server (`6443`) o usar self-hosted runner
- Gestionar y rotar `KUBE_CONFIG_B64` usado por CI/CD

## 7. Gobierno de repositorio

- Activar branch protection en `main`
- Requerir checks de CI/CD para merge
- Configurar CODEOWNERS (opcional)

## Estado

- Implementado en este repo: app instrumentada, Docker/Compose, CI/CD, seguridad, manifests k8s y documentacion.
- Pendiente manual: aprovisionamiento AWS, secretos, TLS, politicas de acceso y operacion en produccion.
