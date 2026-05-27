# Pipeline CI/CD

El pipeline esta definido en `.github/workflows/ci-cd.yml` y cubre calidad, seguridad, pruebas y construccion de imagen.

La publicacion de artefactos se realiza en Nexus:

- Docker hosted para imagenes de contenedor
- Raw hosted para reportes y metadatos de build

## Triggers

- Push a `main` y `develop`
- Pull Request hacia `main` y `develop`
- Tags `v*` para versionado de release
- Ejecucion manual con `workflow_dispatch`

## Etapas

1. `quality-security-tests`
- Instala dependencias de desarrollo (`requirements-dev.txt`)
- Usa Python `3.11` para asegurar compatibilidad de herramientas de seguridad
- Ejecuta lint con Ruff (`ruff check src tests`)
- Ejecuta seguridad SAST con Bandit (`bandit -r src`)
- Ejecuta auditoria de dependencias con pip-audit
- Ejecuta pruebas unitarias con cobertura y reportes JUnit
- Empaqueta y publica reportes en Nexus Raw

2. `build-and-push-image`
- Se ejecuta solo fuera de PR
- Construye imagen Docker con Buildx
- Publica imagen en Nexus Docker (`<nexus-host>:8083/<image>`)
- Etiqueta imagen por:
  - SHA (`sha-...`)
  - Rama (`main`, `develop`)
  - Tag de Git (`v1.0.0`)
  - `latest` cuando el push es a `main`
- Publica tags de imagen en Nexus Raw

3. `deploy-kubernetes`
- Se ejecuta en `push` a `main` y en ejecucion manual (`workflow_dispatch`)
- Configura `kubectl` con `KUBE_CONFIG_B64`
- Aplica manifests de `k8s/`
- Crea/actualiza el secret `nexus-regcred` para pull desde Nexus
- Actualiza la imagen de `todo-api` con el tag inmutable `sha-<GITHUB_SHA>`
- Valida despliegue con `kubectl rollout status`

## Artefactos generados

- Reporte de pruebas JUnit: `reports/pytest-report.xml`
- Cobertura XML: `reports/coverage.xml`
- Cobertura HTML: `htmlcov/`
- Reporte Bandit: `reports/bandit-report.json`
- Reporte pip-audit: `reports/pip-audit-report.json`
- Paquete de calidad en Nexus Raw: `quality-reports-<run>.tar.gz`
- Tags de imagen en Nexus Raw: `image-tags-<run>.txt`
- Despliegue Kubernetes de `todo-api` actualizado al commit de la corrida

## Configuracion requerida en GitHub para este pipeline

Variables (`Repository variables`):

- `NEXUS_REGISTRY` (ej: `ec2-public-dns:8083`)
- `NEXUS_DOCKER_IMAGE` (ej: `ec2-public-dns:8083/todo-api`)
- `NEXUS_RAW_URL` (ej: `http://ec2-public-dns:8081/repository/devops-raw`)

Variable de entorno en workflow:

- `K8S_NAMESPACE` (valor por defecto en workflow: `devops-final`)

Secrets (`Repository secrets`):

- `NEXUS_USERNAME`
- `NEXUS_PASSWORD`
- `KUBE_CONFIG_B64` (kubeconfig del cluster codificado en Base64)

## Politica recomendada de merge

- Requerir estado exitoso del workflow para permitir merge a `main`
- Requerir al menos 1 aprobacion de PR
- Bloquear pushes directos a `main`
