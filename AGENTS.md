# AGENTS.md — crochet-tracker

## Proyecto
Aplicación de escritorio en Python para registrar el avance de un tejido a crochet
siguiendo una guía en PDF: cuenta nudos y filas realizadas y guarda el progreso por
proyecto para retomarlo después.

Estado: MVP en construcción. Hechas las capas `domain/`, `infrastructure/` y `application/`
con sus tests (199 en verde) y la lista de proyectos de `presentation/`; falta el resto de la
interfaz (contadores, notas, guía, deshacer) y el empaquetado, así que todavía no se puede tejer.

## Stack (decidido)
- UI: **PySide6** (Qt, LGPL: válida para distribuir el `.exe`).
- PDF: **pypdfium2** (BSD-3): render de páginas a imagen + extracción de texto.
- Persistencia: **sqlite3** de la stdlib, esquema versionado con `PRAGMA user_version`.
- Empaquetado: **PyInstaller** (`--windowed`).
- Tests: **pytest**; `pytest-qt` solo si se testea la UI.

Reparto: `presentation/` usa Qt; `infrastructure/` contiene el adaptador de pypdfium2 y
el repositorio sqlite3; `domain/` y `application/` no importan ninguna de las tres.

## Comandos
Verificados salvo donde se indica (Python 3.12+; en esta máquina hay un `.venv` con 3.13):
- Instalar: `pip install -e .[dev]`
- Ejecutar: `python -m crochet_tracker` (previsto; `__main__.py` llega con T25/T33)
- Tests: `pytest -q`
- Un solo test: `pytest -q tests/<capa>/test_<modulo>.py::test_<caso>`
- Empaquetar: `pyinstaller --windowed --name CrochetTracker -m crochet_tracker` (previsto)

## Git workflow
- `dev` es la rama de trabajo; `main` solo recibe el MVP, por PR. Los commits y su formato están
  en `docs/constitution.md` §7.
- CI: `.github/workflows/ci.yml` corre `pytest -q` en cada push a `dev`/`main` y en cada PR a `main`.
  El job se llama `tests`.
- Un PR a `main` no se mergea si `tests` no está en verde: la rama `main` está protegida con ese
  check obligatorio, sin pushes directos y sin force-push.
- Antes de cada push: `pytest -q` en local con el mismo Python 3.12.
- Al cerrar el MVP: PR `dev → main`, merge y `git tag -a v0.1.0 -m "MVP"`.
- Historia conocida: `f68fd32` y `20887c8` agrupan tres tareas cada uno (T19–T21 y T22–T24),
  más de lo que admite el «par» de §7. Se decidió no reescribir `dev` ya pusheado; no se repite.

## Arquitectura (capas)
Las dependencias apuntan siempre hacia dentro; una capa externa puede importar a la
interna, nunca al revés.
- `domain/` — modelos y lógica de conteo (nudos, filas). Python puro:
  sin I/O, sin toolkit de UI, sin librería de PDF, sin imports del propio proyecto.
- `application/` — casos de uso y puertos (interfaces): abrir guía, iniciar sesión de
  tejido, incrementar contador, guardar/retomar progreso. Orquesta dominio + puertos.
- `infrastructure/` — implementa los puertos: render/lectura de PDF, persistencia,
  sistema de archivos. Es la única capa que conoce librerías externas de I/O.
- `presentation/` — ventana y widgets de escritorio. No habla con `infrastructure/`
  ni maneja SQL ni PDF directamente: solo con `application/`.

Los puertos viven en `application/` (o `domain/`), no en `infrastructure/`. Los tests
del dominio deben correr sin abrir ventanas ni leer PDFs reales.

## Estilo
- Python 3.12+, type hints en todas las funciones públicas.
- Identificadores en inglés; textos de interfaz y mensajes de usuario en español.

## Reglas
- No añadas dependencias que rompan el reparto de capas (p. ej. que `domain/` importe Qt).
- Librerías externas: preferir las mantenidas y con licencia compatible (MIT/BSD/Apache);
  comprobar licencia antes de adoptar una (AGPL/GPL afecta a la distribución del .exe).
- No añadas dependencias ni cambies el formato de guardado del progreso sin acordarlo
  antes: el progreso de un tejido es dato del usuario y no debe perderse. Todo cambio de
  esquema va con su migración y su subida de `PRAGMA user_version`.
- Cuando existan `docs/constitution.md` y `specs/`, léelos antes de tocar código
  y no modifiques archivos dentro de `specs/` salvo petición explícita.

## Al terminar cualquier tarea
- Ejecuta los tests que existan y confirma en tu respuesta que pasan. Si aún no hay
  tests, dilo explícitamente en lugar de afirmar que el cambio está verificado.
