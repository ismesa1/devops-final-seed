# CALMS aplicado al proyecto

## Culture

- Trabajo via Pull Requests y revision entre pares
- Reglas de merge basadas en calidad automatizada
- Transparencia mediante reportes de pipeline

## Automation

- CI/CD en GitHub Actions
- Lint, seguridad, pruebas y build automatizados
- Versionado de imagen container por tags y SHA

## Lean

- Pipeline dividido por etapas claras
- Feedback rapido en PR con validaciones automáticas
- Artefactos para diagnostico sin repetir ejecuciones manuales

## Measurement

- Cobertura de pruebas (`coverage.xml`, `htmlcov`)
- Metricas de runtime en `/metrics`
- Trazabilidad de builds con tags de imagen y numero de corrida

## Sharing

- Documentacion en carpeta `docs/`
- Configuracion declarativa en `docker-compose.yml`, `.github/workflows/`, `k8s/`
- Dashboards y datasource de observabilidad versionados como codigo
