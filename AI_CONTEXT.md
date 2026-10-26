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
`crochet_tracker/domain/` — existe: `errors.py` (jerarquía `DomainError`) y `project.py`
(`normalize_name`: recorte de extremos, 1..100 caracteres). Faltan `application/`,
`infrastructure/` y `presentation/`.
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
vacío y de más de 100 caracteres, nombres repetidos permitidos). Siguiente paso: T04 (contadores).
La spec está cerrada en revisión 5 (17 RF, 7 RNF, 31 casos límite, 0 dudas abiertas) y el plan
técnico en `specs/001-crochet-mvp/plan.md`.
Descartado para siempre, no aparcado: el porcentaje de avance (no hay total con el que comparar).
Problemas conocidos: solo existen el esqueleto (T01) y los errores de dominio (T02); no hay
lógica ni tests de comportamiento aún. Los comandos de §4 ya se verifican con `pip install -e ".[dev]"` y
`pytest -q`; el resto sigue sin probar.

## 7. Decisiones cerradas (no reabrir sin motivo)
- **Conteo manual**: el usuario marca nudos y filas con botones `+1`/`-1`. El PDF no calcula el
  avance; solo se lee y se muestra. Toda operación tiene inversa y no baja de cero.
- **Local y monousuario**: sin cuentas, sin red, sin telemetría. Funcionar sin conexión es requisito.
- **Un solo documento de reglas por tema**: `AGENTS.md` = cómo se trabaja (comandos, capas);
  `docs/constitution.md` = qué no se negocia; `AI_CONTEXT.md` = qué es el repo y en qué estado está.
- **Sin decisiones abiertas sobre alcance.** Lo que falte por definir se resuelve en la spec, no aquí.
