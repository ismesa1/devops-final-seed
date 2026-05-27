# To-Do API — Semilla para Trabajo Final DevOps

API REST básica de gestión de tareas. **Este es el punto de partida** — su trabajo es construir todo el ecosistema DevOps alrededor.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Info de la API |
| GET | `/tasks` | Listar todas las tareas |
| POST | `/tasks` | Crear tarea (`{"title": "...", "description": "..."}`) |
| GET | `/tasks/<id>` | Obtener una tarea |
| PUT | `/tasks/<id>` | Actualizar tarea |
| DELETE | `/tasks/<id>` | Eliminar tarea |
| GET | `/health` | Estado de salud de app + DB |
| GET | `/metrics` | Metricas en formato Prometheus |

## Ejecutar

```bash
pip install -r requirements.txt
python src/app.py
```

La API corre en `http://localhost:5000`.

## Ejecutar stack completo (Docker + Observabilidad)

```bash
cp .env.example .env
docker compose up -d --build
```

Servicios del sistema:

- Nexus: `http://localhost:8081` (UI), `localhost:8083` (Docker Registry)
- API: `http://localhost:5000`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

## Estado de implementación DevOps

1. **Tests unitarios** — Mínimo 5, en carpeta `tests/` **Implementado**
2. **Dockerfile + docker-compose.yml** — **Implementado**
3. **Pipeline CI/CD** (`.github/workflows/ci-cd.yml`) — **Implementado**
4. **Observabilidad** (logs JSON, `/health`, `/metrics`, Prometheus/Grafana) — **Implementado**
5. **Seguridad** (linting + auditoria de dependencias) — **Implementado**
6. **Kubernetes** (`k8s/`) — **Implementado (bonus)**
7. **Documentación** (`docs/`) — **Implementado**
8. **Artefactos** (imagen versionada + reportes de build) — **Implementado**

Integracion de despliegue:

- El pipeline ahora incluye etapa de CD para aplicar manifiestos Kubernetes y actualizar `todo-api` en `main`

Repositorio de artefactos:

- Docker Registry de Nexus para imagenes
- Repositorio Raw de Nexus para reportes (`quality-reports` e `image-tags`)

Pendientes manuales de infraestructura/productivo en AWS EC2:

- Ver `PENDIENTES_EC2.md`

Lean el documento del trabajo final para los detalles completos de cada requisito.

## Stack

- **Lenguaje:** Python 3.11
- **Framework:** Flask
- **Base de datos:** SQLite (ya incluida, no necesita instalación)
- **Dependencias runtime:** Ver `requirements.txt`
- **Dependencias dev/CI:** Ver `requirements-dev.txt`

## Documentación complementaria

- `docs/pipeline.md`
- `docs/branching.md`
- `docs/observabilidad.md`
- `docs/calms.md`
- `docs/ec2-deploy.md`

---

*DevOps & Automatización — UNAL Sede Manizales — 2026-1*
