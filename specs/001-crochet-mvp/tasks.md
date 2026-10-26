# Tareas 001 — Crochet Tracker MVP

> De `specs/001-crochet-mvp/spec.md` (rev. 5) y `plan.md`. Orden de dependencia: no se empieza una
> tarea hasta que la anterior está en verde. Cada tarea son 20-30 minutos y deja `pytest -q` verde.
> Comandos: ver `AGENTS.md`.

## A. Arranque

- [x] **T01 - Esqueleto del paquete y del proyecto**
  - Archivos: `pyproject.toml`, `crochet_tracker/__init__.py`, `tests/__init__.py`.
  - Hecho cuando: `pip install -e .[dev]` instala sin errores, `python -c "import crochet_tracker"`
    no falla y `pytest -q` informa de 0 tests recogidos (no de error de importación).

- [x] **T02 — Errores de dominio (sin texto de usuario)**
  - Archivos: `crochet_tracker/domain/errors.py`.
  - Hecho cuando: `pytest -q tests/domain/test_errors.py` pasa y los mensajes están en inglés,
    sin ninguna frase de interfaz (constitución §6).

## B. Dominio (Python puro, sin Qt ni sqlite)

- [x] **T03 — Nombre del proyecto** (RF-1, RF-4)
  - Archivos: `domain/project.py`, `tests/domain/test_project_name.py`.
  - Hecho cuando: los tests cubren recorte de extremos, rechazo de vacío/solo espacios, límite de
    100 caracteres y permiso de nombres repetidos (CL-1..CL-6), y `grep -r PySide6 domain/` sale vacío.

- [x] **T04 — Contadores de filas y nudos** (RF-11, RF-12)
  - Archivos: `domain/project.py`, `tests/domain/test_counters.py`.
  - Hecho cuando: subir uno no altera el otro, bajar en cero no cambia el valor ni lanza error, y
    se acepta 100.000 sin recorte (CL-17, CL-18).

- [x] **T05 — Estado terminado** (RF-5)
  - Archivos: `domain/project.py`, `tests/domain/test_finished.py`.
  - Hecho cuando: alternar el estado dos veces deja el valor inicial y contar en un proyecto
    terminado no cambia su estado (CL-28).

- [x] **T06 — Página de la guía** (RF-10)
  - Archivos: `domain/project.py`, `tests/domain/test_page.py`.
  - Hecho cuando: la página nunca baja de 1 y, sabiendo el total de páginas, se recorta a ese total.

- [x] **T07 — Notas** (RF-14, RF-15)
  - Archivos: `domain/note.py`, `tests/domain/test_note.py`.
  - Hecho cuando: se rechaza el texto vacío o solo espacios (CL-19), y editar conserva la fecha de
    creación original.

- [x] **T08 — Deshacer: caducidad y alcance** (RF-16)
  - Archivos: `domain/undo.py`, `tests/domain/test_undo.py`.
  - Hecho cuando: con un reloj falso, la entrada caduca a los 10 minutos, solo hay un paso, no hay
    rehacer y un cambio no deshacible no borra la entrada pendiente.

- [x] **T09 — Deshacer: operaciones inversas** (RF-16)
  - Archivos: `domain/undo.py`, `tests/domain/test_undo_ops.py`.
  - Hecho cuando: deshacer un contador devuelve el valor anterior y deshacer el borrado de una nota
    devuelve texto y fecha originales.

## C. Infraestructura

- [x] **T10 — Carpeta de datos** (RF-17)
  - Archivos: `infrastructure/app_paths.py`, `tests/infrastructure/test_paths.py`.
  - Hecho cuando: con `CROCHET_TRACKER_DATA` definida se usa esa ruta; sin ella se usa la del
    usuario; y la carpeta se crea si no existe.

- [x] **T11 — Esquema y migración** (constitución §5)
  - Archivos: `infrastructure/migrations.py`, `tests/infrastructure/test_migrations.py`.
  - Hecho cuando: una base creada a mano con `user_version = 0` migra a 1, deja `crochet.db.bak`,
    y un paso que falla hace `ROLLBACK` sin tocar los datos.

- [x] **T12 — Repositorio: crear, listar y abrir** (RF-1, RF-2, RF-3)
  - Archivos: `infrastructure/sqlite_repository.py`, `tests/infrastructure/test_repository.py`.
  - Hecho cuando: crear guarda el proyecto, la lista sale ordenada por `updated_at` descendente y
    abrir sin cambios no reordena.

- [x] **T13 — Repositorio: renombrar, terminado, contadores, página** (RF-4, RF-5, RF-10, RF-11, RF-12)
  - Archivos: `infrastructure/sqlite_repository.py`, `tests/infrastructure/test_repository.py`.
  - Hecho cuando: cada `UPDATE` persiste, actualiza `updated_at` y se lee igual tras reabrir la base.

- [x] **T14 — Repositorio: notas** (RF-14, RF-15)
  - Archivos: `infrastructure/sqlite_repository.py`, `tests/infrastructure/test_notes_repo.py`.
  - Hecho cuando: alta, edición y borrado persisten, y las notas salen de más reciente a más antigua.

- [x] **T15 — Repositorio: borrar proyecto** (RF-6)
  - Archivos: `infrastructure/sqlite_repository.py`, `tests/infrastructure/test_delete_repo.py`.
  - Hecho cuando: borrar elimina el proyecto, sus notas (cascada) y su PDF, y la lista ya no lo trae.

- [x] **T16 — Escritura atómica** (RF-13)
  - Archivos: `tests/infrastructure/test_atomicity.py`.
  - Hecho cuando: un `COMMIT` forzado a fallar deja el valor anterior intacto y no hay fila a medias.

- [x] **T17 — Guía en disco** (RF-8, RF-9)
  - Archivos: `infrastructure/guide_store.py`, `tests/infrastructure/test_guide_store.py`.
  - Hecho cuando: copia a un temporal y mueve al final, rechaza lo que no es PDF legible, y un
    archivo ausente se informa como "sin guía" (CL-9..CL-11).

- [x] **T18 — Reloj real** (RF-16)
  - Archivos: `infrastructure/clock.py`, `tests/infrastructure/test_clock.py`.
  - Hecho cuando: el reloj devuelve la hora del sistema y es sustituible por el falso en tests.

## D. Aplicación

- [x] **T19 — Puertos y dobles de test** (RF-3)
  - Archivos: `application/ports.py`, `tests/application/fakes.py`.
  - Hecho cuando: existen `ProjectRepository`, `GuideStore` y `Clock` como `Protocol`, y los dobles
    en memoria implementan los mismos métodos sin importar sqlite ni Qt.

- [x] **T20 — Casos de uso de proyecto** (RF-1..RF-6)
  - Archivos: `application/create_project.py`, `list_projects.py`, `open_project.py`,
    `rename_project.py`, `set_finished.py`, `delete_project.py`, `tests/application/test_projects.py`.
  - Hecho cuando: cada caso de uso se prueba con los dobles y no importa nada de `infrastructure/`.

- [x] **T21 — Casos de uso de contadores y guardado** (RF-11, RF-12, RF-13)
  - Archivos: `application/counters.py`, `tests/application/test_counters.py`.
  - Hecho cuando: si el repositorio falla al guardar, el caso de uso devuelve el valor anterior con
    un error tipado que la vista puede mostrar (RF-13).

- [x] **T22 — Casos de uso de notas** (RF-14, RF-15)
  - Archivos: `application/notes.py`, `tests/application/test_notes.py`.
  - Hecho cuando: añadir, editar y borrar se prueban con los dobles, incluido el fallo al guardar
    (CL-31: se conserva el texto y se informa).

- [x] **T23 — Caso de uso deshacer** (RF-16)
  - Archivos: `application/undo_last_change.py`, `tests/application/test_undo.py`.
  - Hecho cuando: deshace el último cambio de contador o nota, se descarta al cambiar de proyecto y
    no ofrece nada pasados los 10 minutos.

- [x] **T24 — Casos de uso de guía y página** (RF-8, RF-9, RF-10)
  - Archivos: `application/attach_guide.py`, `application/change_page.py`,
    `tests/application/test_guide.py`.
  - Hecho cuando: adjuntar una guía a un proyecto que ya tiene una no hace nada, y cambiar de
    página persiste la página.

## E. Presentación

- [x] **T25 — Ventana principal y navegación** (RF-2, RF-3)
  - Archivos: `presentation/main_window.py`, `presentation/strings.py`, `crochet_tracker/__main__.py`
    (provisional), `tests/presentation/test_navigation.py`.
  - Hecho cuando: se abre la lista, se entra a un proyecto y "← Proyectos" vuelve, y todos los
    textos visibles están en español.

- [x] **T26 — Lista, estado vacío y crear** (RF-1, RF-2)
  - Archivos: `presentation/project_list_view.py`, `tests/presentation/test_list.py`.
  - Hecho cuando: sin proyectos se ve el estado vacío; crear con nombre válido lo abre; con nombre
    vacío avisa y no crea (CL-1, CL-27).

- [x] **T27 — Etiqueta "Terminado" y borrado desde la lista** (RF-2, RF-6)
  - Archivos: `presentation/project_list_view.py`, `tests/presentation/test_list_actions.py`.
  - Hecho cuando: un proyecto terminado se distingue sin desaparecer, y borrar pide confirmación
    con su nombre y solo borra al confirmar.

- [ ] **T28 — Contadores en pantalla** (RF-11, RF-12, RF-13)
  - Archivos: `presentation/project_view.py`, `tests/presentation/test_counters_view.py`.
  - Hecho cuando: `+1`/`-1` cambian el número sin espera perceptible, el botón de bajar está inactivo
    en cero (CL-17) y un fallo de guardado muestra aviso y vuelve al valor anterior.

- [ ] **T29 — Panel de notas** (RF-14, RF-15)
  - Archivos: `presentation/notes_panel.py`, `tests/presentation/test_notes_panel.py`.
  - Hecho cuando: se añade una nota, se edita con Guardar/Cancelar, se borra con confirmación, y
    Cancelar deja el texto anterior (CL-23).

- [ ] **T30 — Aviso de deshacer** (RF-16)
  - Archivos: `presentation/project_view.py`, `tests/presentation/test_undo_banner.py`.
  - Hecho cuando: tras un cambio aparece el aviso, desaparece a los 10 minutos o al deshacer, y no
    aparece tras renombrar, marcar terminado ni cambiar de página.

- [ ] **T31 — Renombrar y marcar terminado dentro del proyecto** (RF-4, RF-5)
  - Archivos: `presentation/project_view.py`, `tests/presentation/test_project_actions.py`.
  - Hecho cuando: el nombre nuevo se ve en la pantalla y en la lista, y el botón de finalizado
    alterna la etiqueta.

## F. Arranque único

- [ ] **T32 — Instancia única** (RF-7, CL-29)
  - Archivos: `infrastructure/single_instance.py`, `tests/infrastructure/test_single_instance.py`.
  - Hecho cuando: el primer proceso obtiene el bloqueo, el segundo no, y liberar el primero permite
    arrancar de nuevo.

- [ ] **T33 — Entrada, argumentos y códigos de salida** (RF-7, plan §3.2)
  - Archivos: `crochet_tracker/__main__.py`, `tests/test_entrypoint.py`.
  - Hecho cuando: sin argumentos arranca; con un argumento desconocido escribe una línea en stderr y
    sale con 2; con la base corrupta sale con 1 y deja constancia en `error.log`.

## G. Guía en pantalla

- [ ] **T34 — Ver y recorrer el PDF** (RF-8, RF-9, RF-10)
  - Archivos: `presentation/guide_view.py`, `tests/presentation/test_guide_view.py`.
  - Hecho cuando: se ve la página guardada (o la primera si nunca se abrió), no se pasa de la
    última, un PDF ilegible muestra aviso y un error de una sola página no bloquea el resto
    (CL-12..CL-14).

## H. Empaquetado

- [ ] **T35 — Ejecutable y comprobación final**
  - Archivos: `CrochetTracker.spec` (generado), `README.md` (sección de uso).
  - Hecho cuando: `pyinstaller --windowed --name CrochetTracker -m crochet_tracker` produce el
    `.exe`, arranca en un equipo sin Python, crea los datos en `%APPDATA%\CrochetTracker` y pasa a
    mano la lista de §8 de la spec (11 criterios).

---

**Cobertura:** RF-1 (T03, T12, T20, T26) · RF-2 (T12, T25, T26, T27) · RF-3 (T12, T19, T25) ·
RF-4 (T03, T13, T20, T31) · RF-5 (T05, T13, T20, T31) · RF-6 (T15, T20, T27) · RF-7 (T32, T33) ·
RF-8 (T17, T24, T34) · RF-9 (T17, T24, T34) · RF-10 (T06, T13, T24, T34) · RF-11 (T04, T13, T21,
T28) · RF-12 (T04, T21, T28) · RF-13 (T16, T21, T28) · RF-14 (T07, T14, T22, T29) · RF-15 (T07,
T14, T22, T29) · RF-16 (T08, T09, T18, T23, T30) · RF-17 (T10, T11).
