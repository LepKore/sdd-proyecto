# Contexto del proyecto

> Última verificación: 2026-10-25

## 1. Propósito del proyecto
Aplicación de escritorio para registrar el avance de un tejido a crochet mientras se sigue
una guía en PDF: cuenta nudos y filas hechas y guarda el progreso por proyecto para retomarlo.
Audiencia: uso personal, un usuario por equipo (cosido a fuego en `docs/constitution.md` §8).
Proyecto educativo: lo mantiene un desarrollador junior.

## 2. Stack tecnológico y arquitectura
Frontend: PySide6 (Qt para escritorio; LGPL).
Backend: Python 3.12+; pypdfium2 para render/extracción del PDF; `sqlite3` de la stdlib.
Empaquetado: PyInstaller (`--windowed`). Tests: `pytest` (`pytest-qt` solo si se testea UI).
Patrones clave: arquitectura en capas con dependencias hacia dentro
(`domain` ← `application` ← `infrastructure`/`presentation`), puertos en `application/`.
Detalle y reparto de responsabilidades: `AGENTS.md`.

## 3. Estructura del proyecto (mapeo)
`/` — `README.md`, `AGENTS.md`, `docs/`, `.gitignore`.
`.github/workflows/ci.yml` — CI: `pytest -q`; el check `tests` es obligatorio para mergear a `main`.
`docs/constitution.md` — principios y puertas de calidad; gobierna specs y PRs.
`specs/` — todavía no existe; cuando exista, no se modifica sin petición explícita.
`crochet_tracker/domain/` — existe: `errors.py` (jerarquía `DomainError`), `project.py`
(`normalize_name` y la entidad `Project` con nombre, contadores, estado terminado y página) y
`note.py` (entidad `Note`: texto y fecha de creación conservada al editar) y `undo.py` (`Undo`:
un solo paso, caducidad de 10 minutos, el inverso es un `Callable`).
`crochet_tracker/infrastructure/` — existe: `app_paths.py` (carpeta de datos, override por
`CROCHET_TRACKER_DATA`), `migrations.py` (esquema v1 y migración con copia `.bak`) y
`sqlite_repository.py` (`SqliteProjectRepository`: `add`, `get`, `list_all`, `save`). Faltan
`application/` y `presentation/`.
Nota para IA: no modificar nada dentro de `specs/` ni `docs/constitution.md` sin pedirlo.

## 4. Comandos críticos
Inicialización: `pip install -e .[dev]` (previsto; aún no hay `pyproject.toml`).
Desarrollo: `python -m crochet_tracker` (previsto).
Testing: `pytest -q`; un solo test: `pytest -q tests/test_<modulo>.py::test_<caso>`.
Lint / typecheck: no configurado todavía.
Deploy: `pyinstaller --windowed --name CrochetTracker -m crochet_tracker` (informativo; requiere confirmación).

## 5. Reglas y convenciones estrictas
Estilo: type hints en funciones públicas; identificadores en inglés, textos de interfaz en español.
Librerías permitidas / prohibidas: MIT/BSD/Apache/ISC; GPL y AGPL prohibidas (se distribuye un `.exe`).
Manejo de errores: se captura donde se puede resolver; `except` vacío es un bug.

## 6. Estado actual y registro de cambios
Completado: repositorio inicial, `AGENTS.md` con stack y capas, `docs/constitution.md` v2.1.0
(7 principios: stack mínimo, la spec manda, lógica sin interfaz, tests, persistencia, idiomas,
commits y ramas) y CI con el check `tests` obligatorio en `main`.
En progreso: `specs/001-crochet-mvp/tasks.md` (35 tareas T01..T35, en orden de dependencia). T01
hecha: `pyproject.toml`, paquete y `tests/` vacíos, instalación editable. T02 hecha:
`domain/errors.py` con `DomainError`, `InvalidProjectName` y `EmptyNoteText`, sin texto de
interfaz. T03 hecha: `domain/project.py` con `normalize_name` (recorte de extremos, rechazo de
vacío y de más de 100 caracteres, nombres repetidos permitidos). T04 y T05 hechas: entidad
`Project` con `change_rows`/`change_knots` (delta, suelo en cero, sin techo) y
`toggle_finished`. T06 hecha: `guide_page` con `change_page` (suelo en 1, tope en la última
página conocida). T07 hecha: `note.py` con `Note(body, created_at)` y `edit` que conserva la fecha.
T08 y T09 hechas: `undo.py` con `Undo` (una entrada, caducidad de 10 min medida con `now`
inyectado, sin rehacer) y `restore_rows`/`restore_knots` en `Project` para el inverso.
T10 hecha: `app_paths.data_dir()`. T11 hecha: `migrations.migrate()` (v0 → v1, copia
`crochet.db.bak`, paso fallido con `ROLLBACK`, base más nueva rechazada con `MigrationError`).
T12 y T13 hechas: `SqliteProjectRepository` con `add`, `get`, `list_all` (orden por `updated_at`
desc) y `save` (todos los campos mutables + `updated_at`); una conexión por operación con WAL,
`synchronous = FULL` y `foreign_keys` activado. T14 y T15 hechas: `add_note`, `list_notes` (más
reciente primero), `save_note` (conserva la fecha) y `delete_note`; `delete_project` borra el
proyecto, sus notas por cascada y su PDF de `<datos>/guides/`, y `Note` gana `id`. T16 hecha:
`tests/infrastructure/test_atomicity.py` fuerza fallos de `COMMIT` y comprueba que no queda nada a
medias. Siguiente paso: T17 (guía en disco).
La spec está cerrada en revisión 5 (17 RF, 7 RNF, 31 casos límite, 0 dudas abiertas) y el plan
técnico en `specs/001-crochet-mvp/plan.md`.
Descartado para siempre, no aparcado: el porcentaje de avance (no hay total con el que comparar).
Problemas conocidos: aún no existen las capas `application/` ni `presentation/`, así que la
aplicación todavía no se puede ejecutar; el progreso ya se guarda, pero solo desde los tests.
`pytest -q` está en verde.

## 7. Decisiones cerradas (no reabrir sin motivo)
- **Conteo manual**: el usuario marca nudos y filas con botones `+1`/`-1`. El PDF no calcula el
  avance; solo se lee y se muestra. Toda operación tiene inversa y no baja de cero.
- **Local y monousuario**: sin cuentas, sin red, sin telemetría. Funcionar sin conexión es requisito.
- **Un solo documento de reglas por tema**: `AGENTS.md` = cómo se trabaja (comandos, capas);
  `docs/constitution.md` = qué no se negocia; `AI_CONTEXT.md` = qué es el repo y en qué estado está.
- **Sin decisiones abiertas sobre alcance.** Lo que falte por definir se resuelve en la spec, no aquí.
