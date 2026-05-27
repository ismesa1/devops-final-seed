# Branching Strategy

Se recomienda un flujo `trunk-based` con rama de integracion liviana:

- `main`: rama estable, siempre desplegable
- `develop`: rama de integracion previa a release
- `feature/<nombre>`: trabajo por funcionalidad
- `hotfix/<nombre>`: correcciones urgentes en produccion

## Flujo de trabajo

1. Crear rama `feature/*` desde `develop`
2. Commits pequenos, con mensajes claros
3. Abrir Pull Request hacia `develop`
4. Exigir pipeline verde (lint, seguridad, tests)
5. Merge por squash
6. Promocionar `develop` a `main` con PR de release
7. Etiquetar release (`vX.Y.Z`) para versionar imagen

## Convencion de versionado

- Se sugiere SemVer: `MAJOR.MINOR.PATCH`
- El tag de Git `vX.Y.Z` debe representar una version desplegable

## Buenas practicas

- No desarrollar en `main`
- No mezclar cambios funcionales y de infraestructura en el mismo PR sin justificacion
- Mantener PR pequenos y revisables
