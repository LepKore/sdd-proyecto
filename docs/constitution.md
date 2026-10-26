# Constitución — crochet-tracker

> v2.1.0 · 2026-10-25
> Siete principios. Si alguno no se puede comprobar mirando el código, está mal escrito y hay que reescribirlo.
> El stack y los comandos están en `AGENTS.md`; aquí solo va lo que no se negocia.
> v2.0.1: aclara el ejemplo del §3 (el porcentaje de avance quedó descartado en la spec 001).
> v2.1.0: añade el §7 (commits y ramas); es `minor` porque añade un principio.

---

## 1. Stack mínimo

Python 3.12+, PySide6, pypdfium2, `sqlite3` de la stdlib y `pytest`. Nada más.
Añadir una dependencia exige justificar en el mismo cambio por qué la stdlib o lo ya instalado
no sirve, y que su licencia sea MIT, BSD, Apache-2.0 o ISC. GPL y AGPL, nunca: el programa se
distribuye como `.exe`.

**Comprobar:** la lista de dependencias del proyecto no tiene nada fuera de esa lista, y todo PR
que añade una explica el motivo.

## 2. La spec manda

No se escribe código sin spec en `specs/`. Si el código contradice la spec, gana la spec. Si la
spec está mal, se corrige la spec **en el mismo cambio, antes del código** — nunca se "arregla"
el código de espaldas a la spec.

**Comprobar:** cada cambio de comportamiento se puede señalar a un trozo de spec.

## 3. La lógica no sabe que existe una interfaz

Contadores y sus límites viven en `domain/`, en Python puro. Ningún import de
Qt, pypdfium2 o `sqlite3` puede aparecer fuera de `infrastructure/` y `presentation/`.
La ventana habla con `application/`, nunca con `infrastructure/` ni con el PDF directamente.

**Comprobar:** los imports de esos tres paquetes, vistos en el diff.

## 4. Los tests no se negocian

Todo cambio ejecuta `pytest -q` y se reporta el resultado real: verde, rojo o "no hay tests
todavía". El dominio se prueba sin abrir ventanas ni leer PDFs reales. Nunca se borra un test,
se marca como `skip` ni se baja un umbral para que la suite pase.

**Comprobar:** el resultado de la suite y el diff de tests — solo se añaden, no se quitan.

## 5. El progreso no se pierde

Guardar es atómico: o queda el cambio completo, o no queda nada. El esquema lleva su versión en
`PRAGMA user_version`, y todo cambio de esquema trae su migración probada sobre una base que ya
existía, con copia del archivo previo. Si la migración falla, se avisa y el original queda intacto.

**Comprobar:** hay un test que parte de una base antigua, migra y comprueba que el progreso sigue ahí.

## 6. Dos idiomas, sin mezclar

Código, nombres de fichero y mensajes de commit en inglés. Textos de interfaz, mensajes de error
para el usuario y documentación en español.

**Comprobar:** `grep` de literales en la UI (español) y de identificadores (inglés).

---

## 7. Commits y ramas

`dev` es la rama de trabajo; `main` solo recibe el MVP terminado, mediante un PR. Un commit por
tarea de `specs/*/tasks.md`; si dos tareas son la misma unidad lógica, se admite un commit por par
y el cuerpo lo dice. Nada de trabajo directo sobre `main`.

Formato del asunto: `<type>(<scope>): <descripción en imperativo> (RF-x, Txx)`.

- `type`: `feat`, `fix`, `test`, `refactor`, `docs`, `chore`.
- `scope`: `domain`, `app`, `infra`, `ui`, `boot`, `build`, `docs`.

El asunto va en inglés (§6) y referencia la tarea y el RF que cubre, para que cada cambio se pueda
señalar a la spec sin abrir el diff. El cuerpo explica el porqué, nunca el qué.

Antes de cada commit: `pytest -q` en verde, o dicho explícitamente que aún no hay tests. El diff
preparado contiene una sola cosa. Nunca se commitea `__pycache__/`, `build/`, `dist/`, `.exe`,
bases de datos, PDFs de prueba ni secretos.

Los cambios de esta constitución van en un PR aparte a `main`, nunca dentro del PR del MVP.

Al mergear el MVP, `main` se etiqueta con su versión (`v0.1.0`) y esa etiqueta es la fuente de la
versión: no se escribe a mano en otro sitio.

**Comprobar:** `git log --oneline dev` muestra un commit por tarea con su `Txx`; `git log --oneline
main` solo muestra merges de PR y tags de versión, no commits de tarea sueltos.

---

## Cómo se cambia esta constitución

Un PR aparte, con el motivo, que suba la versión: `major` si cambia o quita un principio,
`minor` si añade uno, `patch` si solo aclara la redacción. El código no se adapta a la
constitución: es al revés. Y ni `specs/` ni este archivo se tocan sin que se pida.
