# Crochet Tracker

Aplicación de escritorio para anotar el avance de un tejido a crochet mientras sigues una
guía en PDF: cuenta filas y nudos, guarda notas y recuerda la página en la que te quedaste.

## Uso

1. Abre la aplicación: verás la lista de proyectos.
2. «Nuevo proyecto» pide un nombre (hasta 100 caracteres) y lo abre.
3. En la ficha del proyecto: `+1`/`−1` en Filas y Nudos, «Añadir guía» para elegir el PDF,
   «← Página anterior» / «Página siguiente →» para recorrerlo y el panel de notas abajo.
4. Todo se guarda al instante; no hay botón de guardar ni diálogo al cerrar.
5. «← Proyectos» vuelve a la lista. Borrar un proyecto se hace desde la lista y pide confirmación.

Los proyectos terminados llevan la etiqueta «Terminado» y siguen abriéndose, contando y anotando
igual que los demás.

## Dónde están los datos

`%APPDATA%\CrochetTracker` en Windows (`~/.local/share/CrochetTracker` en otros sistemas):

- `crochet.db` — proyectos, contadores, notas y página de cada guía.
- `guides/` — una copia del PDF de cada proyecto.
- `app.lock` — evita abrir dos ventanas sobre los mismos datos.
- `error.log` — solo aparece si el arranque falló.

La variable `CROCHET_TRACKER_DATA` cambia esa carpeta (útil para llevar la aplicación en un pendrive
o para probar). Para hacer una copia de seguridad basta con copiar la carpeta entera con la
aplicación cerrada.

## Desarrollo

Requiere Python 3.12 o superior.

```
pip install -e .[dev]
python -m crochet_tracker
pytest -q
```

## Generar el ejecutable

PyInstaller no acepta `-m`, así que el punto de entrada es el propio `crochet_tracker/__main__.py`:

```
pip install pyinstaller
pyi-makespec --windowed --name CrochetTracker --paths . crochet_tracker/__main__.py
pyinstaller --noconfirm CrochetTracker.spec
```

El resultado queda en `dist\CrochetTracker\CrochetTracker.exe`. El `.spec` ya está versionado, así
que a partir de ahí basta con `pyinstaller --noconfirm CrochetTracker.spec`.
