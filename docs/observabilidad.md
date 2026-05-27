# Observabilidad

La API incluye:

- Logs estructurados en JSON (stdout)
- Health check en `/health`
- Metricas Prometheus en `/metrics`
- Stack local con Prometheus y Grafana por Docker Compose

## Logs estructurados

Se registran eventos HTTP con campos:

- `timestamp`
- `level`
- `logger`
- `message`
- `http_method`
- `path`
- `status_code`
- `duration_ms`

Tambien se registran eventos de negocio:

- `task_created`
- `task_updated`
- `task_deleted`

## Health endpoint

`GET /health`

Respuesta exitosa:

```json
{
  "status": "ok",
  "database": "ok",
  "version": "1.0.0"
}
```

Si falla la conexion a SQLite, responde `503`.

## Metricas

`GET /metrics`

Expuestas via `prometheus-flask-exporter`:

- Conteo de requests HTTP
- Latencia de requests
- Codigos de estado
- Informacion de aplicacion (`app_info`)

## Prometheus y Grafana

En Compose:

- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

Credenciales por defecto de Grafana en local:

- Usuario: `admin`
- Password: `admin`

Se recomienda cambiar credenciales en cualquier entorno compartido.
