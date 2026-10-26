# Plan técnico 001 — Crochet Tracker MVP

> Spec: `specs/001-crochet-mvp/spec.md` (revisión 5). Constitución: `docs/constitution.md` v2.0.1.
> Este plan no añade comportamiento: cada decisión existe para cumplir un RF de la spec.

---

## 1. Estructura de módulos

Las dependencias apuntan hacia dentro (constitución §3): `presentation` → `application` → `domain`.
`infrastructure` implementa los puertos de `application` y es la única capa que importa `sqlite3`,
`pypdfium2`, Qt o el sistema de archivos.

```
crochet_tracker/
  __main__.py              arranque, argumentos y códigos de salida .......... RF-7
  domain/
    project.py             nombre, contadores, estado, página ........... RF-1,2,4,5,11,12,17
    note.py                texto, fecha, reglas de la nota .............. RF-14,15
    undo.py                deshacer de un paso con caducidad ........... RF-16
    errors.py              errores de dominio en inglés, sin texto de UI
  application/
    ports.py               ProjectRepository, GuideStore, Clock (Protocol) ... RF-3,8,13
    create_project.py      ................................................ RF-1
    list_projects.py       ................................................ RF-2
    open_project.py        ................................................ RF-3,17
    rename_project.py      ................................................ RF-4
    set_finished.py        ................................................ RF-5
    delete_project.py      ................................................ RF-6
    attach_guide.py        ................................................ RF-8,9
    change_page.py         ................................................ RF-10,13
    counters.py            subir y bajar contadores ....................... RF-11,12,13
    notes.py               añadir, editar, borrar ......................... RF-14,15
    undo_last_change.py    ................................................ RF-16
  infrastructure/
    app_paths.py           carpeta de datos y de guías .................... RF-17
    single_instance.py     bloqueo de instancia única .................... RF-7
    sqlite_repository.py   persistencia ................................... RF-2,3,13,17
    migrations.py          esquema versionado y migración ................ RNF-1
    guide_store.py         copia y borrado del PDF ....................... RF-8,9,6
    clock.py               reloj real para el deshacer ................... RF-16
  presentation/
    main_window.py         conmutador lista ↔ proyecto ................... RF-2,3
    project_list_view.py   lista, crear, borrar .......................... RF-1,2,6
    project_view.py        nombre, estado, contadores, notas, deshacer .... RF-4,5,11,12,14,15,16
    guide_view.py          render de páginas y navegación ................ RF-8,9,10
    notes_panel.py         ................................................ RF-14,15
    strings.py             todos los textos en español ................... RNF-5
pyproject.toml             dependencias y entry point
tests/                     ver §6
```

Regla de dependencia comprobable: `grep` de `PySide6|pypdfium2|sqlite3|pathlib` solo aparece en
`infrastructure/` y `presentation/` (constitución §3).

---

## 2. Modelo de datos (sqlite3)

Una sola base, `crochet.db`, con `PRAGMA user_version = 1`, `journal_mode = WAL` y
`synchronous = FULL` para que cada escritura sea completa o inexistente (RNF-1, constitución §5).

### 2.1 Esquema

```sql
PRAGMA user_version = 1;

CREATE TABLE project (
    id            INTEGER PRIMARY KEY,
    name          TEXT    NOT NULL,              -- 1..100 caracteres ya recortados
    is_finished   INTEGER NOT NULL DEFAULT 0,    -- 0/1
    rows_done     INTEGER NOT NULL DEFAULT 0,    -- >= 0, sin techo (CL-18)
    knots_done    INTEGER NOT NULL DEFAULT 0,    -- >= 0, sin techo (CL-18)
    guide_page    INTEGER NOT NULL DEFAULT 1,    -- página recordada (RF-10)
    guide_file    TEXT,                          -- nombre del PDF copiado, NULL si no hay guía
    created_at    INTEGER NOT NULL,              -- epoch UTC en segundos
    updated_at    INTEGER NOT NULL               -- orden de la lista (RF-2)
);

CREATE TABLE note (
    id          INTEGER PRIMARY KEY,
    project_id  INTEGER NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    body        TEXT    NOT NULL,
    created_at  INTEGER NOT NULL                 -- se conserva al editar (RF-15)
);

CREATE INDEX idx_project_updated ON project(updated_at DESC, id DESC);
CREATE INDEX idx_note_project ON note(project_id, created_at DESC, id DESC);
```

El PDF **no** se guarda como BLOB: se copia a `<datos>/guides/<id>-<uuid>.pdf` y la base solo
guarda el nombre (RF-8). Un PDF de 200 MB dentro de la base haría cada copia de seguridad y cada
`VACUUM` igual de grandes que el PDF.

`guide_page` se valida `>= 1` en el dominio; el máximo solo se conoce al abrir el PDF, así que se
recorta en la vista (RF-10). Nada de tablas de auditoría, ni de usuarios, ni de historial: el
deshacer vive en memoria (RF-16).

### 2.2 Ejemplo

```sql
INSERT INTO project VALUES
  (1, 'Bufanda de lana', 0, 42, 1680, 7, '1-8f3a.pdf', 1761400000, 1761480000),
  (2, 'Amigurumi pulpo', 1, 30, 900,  1, NULL,          1761000000, 1761200000);

INSERT INTO note VALUES
  (1, 1, 'Se acabó la lana gris: la siguiente fila va en beige.', 1761400100),
  (2, 1, 'Cambié a aguja de 4 mm, queda más apretado.',           1761470000);
```

Traducido a lo que ve el usuario: dos proyectos, el segundo terminado y sin guía; el primero con
guía en la página 7, 42 filas, 1680 nudos y dos notas. La lista los muestra en ese orden porque
`updated_at` del primero es mayor (RF-2). Abrir un proyecto sin cambiar nada **no** toca
`updated_at`; pasar de página sí, porque es un cambio guardado (RF-2, RF-10).

### 2.3 Escrituras

Cada acción del usuario es una transacción (`BEGIN IMMEDIATE … COMMIT`) que toca una fila:

| Acción | Sentencia | RF |
|---|---|---|
| Crear | `INSERT INTO project …` | RF-1 |
| Renombrar | `UPDATE project SET name=?, updated_at=?` | RF-4 |
| Terminado | `UPDATE project SET is_finished=?, updated_at=?` | RF-5 |
| Contador ±1 | `UPDATE project SET rows_done=rows_done+? …` | RF-11, RF-12 |
| Página | `UPDATE project SET guide_page=?, updated_at=?` | RF-10, RF-13 |
| Guía | `UPDATE project SET guide_file=?` (tras copiar el archivo) | RF-8 |
| Nota | `INSERT/UPDATE/DELETE note` | RF-14, RF-15 |
| Borrar proyecto | `DELETE FROM project` (cascada a notas) y luego el PDF | RF-6 |
| Deshacer | la sentencia inversa del último cambio | RF-16 |

Si el `COMMIT` falla, se hace `ROLLBACK` y la vista vuelve al último valor guardado mostrando el
aviso (RF-13, RNF-2). La copia del PDF se escribe en `<datos>/tmp/` y se mueve con `os.replace`
cuando está completa: nunca hay un PDF a medias (CL-10, CL-11, CL-30).

---

## 3. Contrato de invocación (CLI)

La spec no tiene ningún RF de CLI y el `.exe` se empaqueta `--windowed`, así que la aplicación
**no ofrece comandos**: se define el contrato mínimo del punto de entrada, que es lo único que
existe y lo que los tests necesitan fijar.

### 3.1 Comando

```
python -m crochet_tracker
```

- Sin subcomandos, sin opciones, sin argumentos posicionales. **RF cubiertos:** todos (es el
  arranque de la aplicación).
- `-m` es el único modo soportado; el `.exe` empaquetado se ejecuta sin argumentos.

### 3.2 Salidas

| Situación | stdout | stderr | Código |
|---|---|---|---|
| Arranque normal, cierre por el usuario | vacío | vacío | `0` |
| Segunda instancia (RF-7): avisa en un diálogo y se cierra | vacío | vacío | `0` |
| Error fatal: base corrupta o de versión más nueva (CL-26), sin permisos (CL-25) | vacío | `crochet_tracker: <motivo>` (una línea) | `1` |
| Argumento no reconocido | vacío | `crochet_tracker: argumento no reconocido: <arg>` | `2` |

Los mensajes de stderr van en inglés porque son diagnóstico, no interfaz (constitución §6); el
texto que ve el usuario siempre es un diálogo en español.

Con `--windowed` no hay consola: los códigos y stderr solo sirven a los tests y al empaquetado.
Es una limitación aceptada, no un fallo, y por eso no se documenta como interfaz de usuario.

### 3.3 Descartado

Una CLI de administración (`list`, `export`, `delete`) con `argparse`. Se descarta porque la spec
pone la exportación fuera de alcance (§7), porque RF-6 exige confirmación con el nombre y un
diálogo, y porque duplicaría en texto cada caso de uso de `application/`. Si algún día hace falta,
entra como RF nuevo, no como atajo.

---

## 4. Decisiones técnicas

### 4.1 sqlite3 frente a un fichero JSON

**Decisión:** una base sqlite con `user_version`.
**Motivo:** RNF-1 y constitución §5 piden escritura atómica y migración probada sobre datos
existentes; sqlite da transacción y versión de esquema sin escribir código. Con un JSON, cada
`+1` reescribiría el archivo entero y una caída a mitad lo dejaría truncado, que es lo que RF-13
y CL-24 prohíben. Además el JSON tendría que versionarse a mano.
**Descartado:** `json` + `os.replace` atómico. Se paga menos al empezar y más en cada guardado y
en cada migración.

### 4.2 Carpeta de datos: `%APPDATA%\CrochetTracker`

**Decisión:** `app_paths.py` resuelve `%APPDATA%\CrochetTracker` en Windows (y `~/.local/share/…`
fuera), con la variable `CROCHET_TRACKER_DATA` como override para los tests.
**Motivo:** RNF-7 (datos del usuario que sobreviven a reinstalar) y CL-26 (hay que poder nombrar
la carpeta). `os.environ` + `pathlib` son stdlib: no rompe la constitución §1.
**Descartado:** `platformdirs` (dependencia nueva para tres líneas) y guardar junto al `.exe`
(Program Files no es escribible sin permisos y el desinstalador se llevaría el progreso).

### 4.3 Instancia única: `QLockFile`

**Decisión:** `infrastructure/single_instance.py` usa `QLockFile` en `<datos>/app.lock`; si no se
puede bloquear, la aplicación avisa y se cierra (RF-7, CL-29).
**Motivo:** forma parte de PySide6, que ya es dependencia (§1), detecta bloqueos huérfanos de un
cierre forzado y funciona en las tres plataformas. La constitución §3 permite Qt en
`infrastructure/` y `presentation/`.
**Descartado:** `socket` a un puerto fijo (choca con otro programa y con el firewall), un archivo
`O_CREAT|O_EXCL` (queda huérfano tras un cierre forzado y hay que inventar un protocolo de
limpieza) y `msvcrt.locking` (solo Windows).

### 4.4 Deshacer: instantánea inversa en memoria

**Decisión:** `undo.py` guarda **una** entrada con la operación inversa y la hora; se descarta al
caducar (10 min), al deshacer, al volver a la lista o al cerrar (RF-16).
**Motivo:** con un paso basta para el error real (un toque de más) y no obliga a versionar filas.
El reloj se inyecta, así que la caducidad se prueba sin esperar diez minutos.
**Descartado:** una pila de historial y una tabla de auditoría; ambas piden más código y más
esquema para un caso que la spec limita a un paso.

Esbozo:

```
al cambiar algo deshacible (contador o nota):
    guardar {inverso, momento}
al pulsar deshacer:
    si no hay entrada o (ahora - momento) > 10 min: no ofrecer
    aplicar el inverso en una transacción
    borrar la entrada            # un solo paso, sin rehacer
al cambiar algo no deshacible (nombre, estado, página): no toca la entrada
```

### 4.5 PDF: pypdfium2 en `infrastructure`, render en `presentation`

**Decisión:** `guide_store.py` copia y valida el archivo; `guide_view.py` pide la página al
documento y la pinta. Un fallo de una página se captura y se muestra en esa página (CL-14).
**Motivo:** RF-8 y RF-10; y §3 prohíbe que el dominio sepa que hay un PDF.
**Descartado:** extraer el texto del PDF para "leer el patrón": está fuera de alcance (§7) y
convertiría un visor en un intérprete de patrones.

### 4.6 Notas y deshacer, sin caché propia

**Decisión:** las notas se leen de la base cada vez que se abre el proyecto; el panel guarda solo
el texto en edición. Las notas se guardan al confirmar (RF-15), no mientras se escribe.
**Motivo:** no hay dos fuentes de verdad que puedan discrepar tras un guardado fallido (CL-31).
**Descartado:** un modelo en memoria sincronizado a mano con la base.

### 4.7 Empaquetado

**Decisión:** PyInstaller `--windowed --name CrochetTracker -m crochet_tracker`, con la carpeta de
datos fuera del paquete.
**Motivo:** AGENTS.md y RNF-7; actualizar la aplicación no puede borrar el progreso.
**Descartado:** `--onefile` con los datos dentro del ejecutable temporal.

---

## 5. Orden de implementación

Cada paso deja la suite en verde y se puede revisar solo (constitución §2, §4).

1. `domain/` completo con sus tests: nombre, contadores, página, notas, deshacer. Sin Qt.
2. `infrastructure/sqlite_repository.py` + `migrations.py` + tests sobre `tmp_path`.
3. `application/` con puertos y casos de uso, probados con dobles en memoria.
4. `presentation/project_list_view.py` (RF-1, RF-2, RF-6) sobre lo anterior.
5. `presentation/project_view.py` (RF-4, RF-5, RF-11, RF-12, RF-13, RF-14, RF-15, RF-16).
6. `infrastructure/single_instance.py` y `__main__.py` (RF-7, códigos de salida).
7. `guide_store.py` + `guide_view.py` (RF-8, RF-9, RF-10).
8. Empaquetado y comprobación en limpio de §8 de la spec.

---

## 6. Estrategia de tests

`pytest -q` en cada cambio (constitución §4). El dominio no abre ventanas ni lee PDFs reales.

| Nivel | Qué se prueba | Archivo | RF |
|---|---|---|---|
| Dominio | validación de nombre 1..100, recorte de extremos, nombres repetidos | `tests/domain/test_project_name.py` | RF-1, RF-4, CL-1..CL-6 |
| Dominio | contadores +1/-1, nunca por debajo de cero, sin techo | `tests/domain/test_counters.py` | RF-11, RF-12, CL-17, CL-18 |
| Dominio | deshacer: caducidad con reloj falso, un solo paso, sin rehacer, no lo anula un cambio no deshacible | `tests/domain/test_undo.py` | RF-16 |
| Dominio | notas: texto vacío rechazado, fecha de creación conservada al editar | `tests/domain/test_note.py` | RF-14, RF-15, CL-19 |
| Aplicación | casos de uso con repositorio y guía falsos en memoria | `tests/application/` | RF-1..RF-6, RF-8, RF-9, RF-14..RF-16 |
| Infraestructura | CRUD real sobre base temporal; orden de la lista; abrir no reordena | `tests/infrastructure/test_repository.py` | RF-2, RF-3, RF-17 |
| Infraestructura | escritura atómica: commit fallido deja el valor anterior | `tests/infrastructure/test_atomicity.py` | RF-13, CL-24, CL-25 |
| Infraestructura | migración: base con `user_version = 0` y datos → migra → datos intactos y copia `.bak` | `tests/infrastructure/test_migrations.py` | Constitución §5 |
| Infraestructura | guía: copia completa y borrado; archivo ausente se trata como sin guía | `tests/infrastructure/test_guide_store.py` | RF-8, RF-9, CL-9..CL-11 |
| Arranque | argumento inválido → código 2 y una línea en stderr; segunda instancia → diálogo y 0 | `tests/test_entrypoint.py` | RF-7, §3.2 |
| Interfaz (`pytest-qt`, opcional) | humo: crear proyecto, abrir, `+1`, volver a la lista | `tests/presentation/test_navigation.py` | RF-1, RF-2, RF-3 |

Lo que la spec marca `[manual]` (botones, diálogos, navegación del PDF) se comprueba a mano con la
lista de §8 de la spec y no se finge con tests de interfaz que solo comprueban que existe un
widget. `pytest-qt` solo se instala si se escribe ese test de humo; hasta entonces no entra en las
dependencias.

### Migración (constitución §5)

`migrations.py` aplica los pasos en orden dentro de una transacción y sube `user_version`. Antes de
migrar copia la base a `crochet.db.bak`. Si un paso falla: `ROLLBACK`, se conserva la copia, se
avisa al usuario con la ruta del archivo y no se toca nada (CL-26). El test parte de una base
creada a mano con `user_version = 0`, sin tablas, y comprueba que tras migrar se puede crear un
proyecto. Cuando exista un esquema v2, el mismo test se extiende con datos de v1.

---

## 7. Riesgos

- **`QLockFile` y carpeta de datos de solo lectura:** si `%APPDATA%` no es escribible, no hay
  bloqueo ni base. Se trata como error fatal (código 1) con mensaje en español; no se intenta
  degradar a "sin bloqueo", porque dos instancias rompen el principio §5 de la constitución.
- **PDF enorme:** sin límite de tamaño (CL-15), la memoria puede dispararse al renderizar. Se
  renderiza solo la página visible, nunca el documento entero.
- **`--windowed` sin consola:** un fallo de arranque antes de crear la ventana no se ve. Se
  escribe el error también en `<datos>/error.log` para poder diagnosticarlo.
