# Spec 001 — Crochet Tracker MVP

> Estado: revisión 5 · 2026-10-25
> Alcance de este documento: **el qué y el porqué**. El stack, la arquitectura y los nombres de
> archivos no van aquí; van en el plan. Sujeto a `docs/constitution.md` v2.0.1.
>
> Cada criterio de aceptación lleva marca de cómo se comprueba:
> `[auto]` = se puede probar sin abrir ventanas · `[manual]` = solo se comprueba usando la interfaz.

---

## 1. Contexto y objetivo

Quien teje a crochet sigue una guía (un PDF con el patrón) y va contando lo que lleva hecho.
Hoy eso se lleva en papel, en la memoria o en el móvil, y se pierde: al retomar el tejido días
después nadie recuerda en qué fila se quedó, ni por qué cambió de aguja, ni dónde dejó la nota
de que se quedó sin lana de un tono.

**Objetivo:** una aplicación de escritorio donde una persona crea un proyecto de crochet, adjunta
la guía en PDF, apunta cuántas filas y cuántos nudos lleva hechos, y deja notas para su yo del
futuro. Al volver a abrir la aplicación, todo sigue donde estaba.

**Criterio de éxito:** cerrar la aplicación a mitad de un tejido y volver tres semanas después,
con la misma guía a la vista y los contadores exactamente como se dejaron, sin haber tenido que
rehacer ninguna cuenta.

**Qué NO es:** no interpreta el patrón, no cuenta por ti, no teje, no sincroniza entre
dispositivos y no sustituye a la guía: la muestra.

---

## 2. Usuarios

| Usuario | Quién es | Qué necesita |
|---|---|---|
| Tejedora/tejedor (único y principal) | Persona con un proyecto de crochet en curso, sin conocimientos técnicos | Ver su guía, saber por dónde va, anotar lo que no quiere olvidar, retomarlo otro día |
| Autor del proyecto (educativo) | Desarrollador junior que mantiene la aplicación | Una funcionalidad pequeña, cerrada y comprobable; sin sorpresas |

Un solo usuario por equipo, y una sola instancia de la aplicación a la vez. No hay cuentas, ni
sesiones, ni perfiles, ni uso compartido.

---

## 3. Historias de usuario

- **HU-1.** Como tejedora, quiero crear un proyecto con un nombre para separar un tejido de otro.
- **HU-2.** Como tejedora, quiero adjuntar el PDF de la guía a un proyecto para tenerlo a mano
  dentro de la aplicación.
- **HU-3.** Como tejedora, quiero ver la guía y moverme por sus páginas sin salir del proyecto.
- **HU-4.** Como tejedora, quiero marcar filas y nudos hechos con un toque para no perder la cuenta.
- **HU-5.** Como tejedora, quiero deshacer un toque de más sin estropear la cuenta entera.
- **HU-6.** Como tejedora, quiero dejar una nota con la fecha para acordarme de algo al retomar.
- **HU-7.** Como tejedora, quiero corregir o borrar una nota que ya no sirve.
- **HU-8.** Como tejedora, quiero retomar el proyecto justo donde lo dejé, días después.
- **HU-9.** Como tejedora, quiero renombrar un proyecto si el nombre que puse no me sirve.
- **HU-10.** Como tejedora, quiero marcar un proyecto como terminado para distinguirlo del que
  tengo entre manos.
- **HU-11.** Como tejedora, quiero borrar un proyecto que ya no quiero, sin riesgo de borrar el
  equivocado.
- **HU-12.** Como tejedora, quiero volver a la lista de proyectos sin cerrar la aplicación.
- **HU-13.** Como tejedora, quiero deshacer el último cambio si me he equivocado, sin tener que
  arreglarlo a mano contando hacia atrás.

---

## 4. Requisitos funcionales

Notación EARS en español. *El sistema* = la aplicación. Los criterios son comprobables uno a uno.

### 4.1 Proyectos

**RF-1 — Crear un proyecto.**
El sistema deberá permitir crear un proyecto indicando un nombre de entre 1 y 100 caracteres.
Criterios de aceptación:
- Cuando el usuario confirme la creación con un nombre válido, el sistema deberá añadir el
  proyecto a la lista y abrirlo. `[manual]`
- Cuando el usuario intente crear un proyecto con el nombre vacío o solo con espacios, el sistema
  deberá rechazar la creación y mostrar un mensaje que indique que falta el nombre. `[auto]`
- Cuando el usuario escriba un nombre de más de 100 caracteres, el sistema deberá impedir seguir
  escribiendo más allá del límite. `[manual]`
- Cuando el usuario cancele la creación, el sistema deberá cerrar el formulario sin crear nada. `[manual]`
- Mientras el nombre repita el de un proyecto existente, el sistema deberá aceptarlo sin aviso y
  sin impedir la creación. `[auto]`

**RF-2 — Ver la lista de proyectos.**
El sistema deberá mostrar todos los proyectos existentes con su nombre, la fecha de su última
modificación y si están terminados, ordenados por última modificación, el más reciente arriba.
Criterios de aceptación:
- Cuando el usuario abra la aplicación, el sistema deberá mostrar la lista de proyectos, o un
  mensaje de bienvenida que invite a crear el primero si no hay ninguno. `[manual]`
- Mientras un proyecto esté marcado como terminado, el sistema deberá mostrar la etiqueta
  "Terminado" junto a su nombre, sin ocultarlo ni impedir abrirlo. `[manual]`
- Cuando un proyecto se modifique, el sistema deberá subirlo al principio de la lista. `[auto]`
- Cuando el usuario abra un proyecto para mirarlo sin cambiar nada, el sistema no deberá contarlo
  como modificación ni reordenar la lista por ello. `[auto]`
- Cuando el nombre de un proyecto no quepa en la lista, el sistema deberá recortarlo con puntos
  suspensivos y mostrar el nombre completo al pasar el ratón por encima. `[manual]`

**RF-3 — Abrir un proyecto y volver a la lista.**
Cuando el usuario seleccione un proyecto de la lista, el sistema deberá abrirlo mostrando su
nombre, sus contadores, su guía (si la tiene) y sus notas.
Criterios de aceptación:
- Cuando el proyecto se abra, el sistema deberá mostrar los valores de contadores, notas y página
  de la guía tal como quedaron guardados. `[manual]`
- Mientras haya un proyecto abierto, el sistema deberá mantener uno solo a la vez: volver a la
  lista cierra el proyecto abierto. `[manual]`
- Cuando el usuario pulse "← Proyectos", el sistema deberá volver a la lista sin cerrar la
  aplicación y sin perder ningún cambio. `[manual]`

**RF-4 — Renombrar un proyecto.**
El sistema deberá permitir cambiar el nombre de un proyecto, con las mismas reglas de nombre que
al crearlo y permitiendo repetir un nombre existente.
Criterios de aceptación:
- Cuando el usuario quiera cambiar el nombre, el sistema deberá ofrecerlo dentro de la pantalla del
  proyecto abierto, nunca desde la lista. `[manual]`
- Cuando el usuario confirme un nombre nuevo válido, el sistema deberá guardarlo y mostrarlo en la
  lista y en la pantalla del proyecto. `[auto]`
- Cuando el usuario confirme un nombre vacío o solo con espacios, el sistema deberá conservar el
  nombre anterior y avisar de que falta el nombre. `[auto]`
- Cuando el usuario renombre y vuelva a abrir el proyecto, el sistema deberá mostrar el nombre
  nuevo. `[auto]`

**RF-5 — Marcar y desmarcar un proyecto como terminado.**
Criterios de aceptación:
- Cuando el usuario pulse el botón de finalizado, el sistema deberá alternar el estado del proyecto
  abierto entre terminado y en curso, y guardarlo en el acto. `[manual]`
- Cuando el usuario marque un proyecto como terminado, el sistema deberá mostrar la etiqueta
  "Terminado" en la lista y en la pantalla del proyecto. `[manual]`
- Mientras un proyecto esté terminado, el sistema deberá seguir permitiendo contar filas y nudos,
  añadir notas y abrirlo, sin cambiar su estado por ello. `[manual]`
- Cuando el usuario desmarque un proyecto como terminado, el sistema deberá guardar el cambio y
  quitar la etiqueta. `[auto]`

**RF-6 — Borrar un proyecto.**
El sistema deberá permitir borrar un proyecto, con confirmación previa que muestre su nombre.
Criterios de aceptación:
- Si el usuario confirma el borrado, entonces el sistema deberá eliminar de forma permanente el
  proyecto, su progreso, su guía copiada y sus notas, y quitarlo de la lista. `[auto]`
- Si el usuario cancela, entonces el sistema deberá conservar el proyecto íntegro. `[auto]`
- El sistema no deberá ofrecer borrar un proyecto desde la pantalla del proyecto abierto: el
  borrado se hace desde la lista. `[manual]`
- Cuando el usuario borre un proyecto de la lista, el sistema deberá quitarlo de la lista sin dejar
  ningún dato suyo a la vista. `[manual]`
- Cuando el usuario vuelva a abrir la aplicación tras borrar, el sistema no deberá mostrar el
  proyecto borrado. `[auto]`

**RF-7 — Una sola instancia de la aplicación.**
Criterios de aceptación:
- Cuando el usuario abra la aplicación con otra instancia ya en marcha, el sistema deberá avisar de
  que ya hay una abierta, deberá cerrarse y no deberá abrir una segunda ventana sobre los mismos
  datos. `[manual]`
- Mientras no haya ninguna instancia abierta, el sistema deberá arrancar con normalidad. `[manual]`

### 4.2 Guía en PDF

**RF-8 — Adjuntar la guía.**
El sistema deberá permitir elegir un archivo PDF del equipo al crear un proyecto y, después, desde
la pantalla del proyecto, pero solo mientras el proyecto no tenga guía. La guía se guarda dentro de
los datos del proyecto, de forma que siga disponible aunque el archivo original se mueva o se borre.
Criterios de aceptación:
- Cuando el usuario elija un PDF legible, el sistema deberá copiarlo al proyecto y mostrarlo como
  su guía. `[manual]`
- Cuando el usuario cancele la selección de archivo, el sistema deberá dejar el proyecto sin guía y
  sin mensaje de error. `[manual]`
- Cuando el usuario cancele mientras el PDF se está preparando, el sistema deberá detener la
  operación, no dejar ningún archivo a medias y dejar el proyecto como estaba. `[manual]`
- Si el archivo elegido no es un PDF o no se puede leer, entonces el sistema deberá avisar con un
  mensaje claro y dejar el proyecto como estaba, sin guía nueva. `[manual]`
- Mientras el proyecto ya tenga guía, el sistema no deberá ofrecer ninguna forma de cambiarla ni de
  añadir una segunda. `[manual]`
- El sistema deberá aceptar archivos de cualquier tamaño y no deberá imponer un tiempo máximo de
  espera. `[manual]`

**RF-9 — Proyecto sin guía.**
Mientras un proyecto no tenga guía, el sistema deberá permitir usarlo con normalidad y ofrecer la
opción de añadirla.
Criterios de aceptación:
- Cuando se abra un proyecto sin guía, el sistema deberá mostrar sus contadores y notas, y un aviso
  de que todavía no hay guía. `[manual]`
- Cuando el usuario añada la guía a un proyecto existente, el sistema deberá mostrarla sin exigir
  reiniciar la aplicación. `[manual]`
- Cuando la guía copiada de un proyecto haya desaparecido del equipo, el sistema deberá tratarlo
  como un proyecto sin guía, avisar de ello y permitir añadir otra. `[manual]`

**RF-10 — Ver y recorrer la guía.**
Criterios de aceptación:
- Cuando el usuario abra un proyecto con guía que ya se abrió antes, el sistema deberá mostrar la
  página en la que se quedó. `[auto]`
- Cuando el usuario abra un proyecto con guía que nunca se abrió, el sistema deberá mostrar la
  primera página. `[auto]`
- Cuando el usuario pida la página siguiente o la anterior, el sistema deberá avanzar o retroceder
  una página sin salir del proyecto y guardar la página nueva en el acto. `[manual]`
- Mientras el usuario esté en la última página, el sistema deberá impedir avanzar más allá. `[auto]`
- Si una sola página no se puede dibujar, entonces el sistema deberá avisar en esa página y
  permitir seguir pasando a las demás. `[manual]`

### 4.3 Contadores

**RF-11 — Contador de filas y contador de nudos, independientes.**
El sistema deberá llevar, por proyecto, dos contadores totales independientes: filas realizadas y
nudos realizados.
Criterios de aceptación:
- Cuando el usuario incremente el contador de filas, el sistema deberá aumentarlo en uno y no
  alterar el de nudos. `[auto]`
- Cuando el usuario incremente el contador de nudos, el sistema deberá aumentarlo en uno y no
  alterar el de filas. `[auto]`
- Cuando el usuario pulse varias veces seguidas, el sistema deberá contar una por pulsación y no
  repetir el incremento por mantener pulsado. `[manual]`
- Cuando el usuario vuelva a abrir el proyecto, el sistema deberá mostrar los dos valores en el
  estado en que quedaron. `[auto]`

**RF-12 — Reducir un contador en uno.**
El sistema deberá permitir reducir cada contador en uno.
Criterios de aceptación:
- Cuando el usuario reduzca un contador mayor que cero, el sistema deberá disminuirlo en uno y
  guardar el cambio. `[auto]`
- Mientras un contador esté en cero, el sistema no deberá permitir bajarlo más y no deberá mostrar
  ningún error. `[auto]`

**RF-13 — Guardado inmediato del progreso.**
Cuando el usuario cambie un contador, la página de la guía, el nombre, el estado o la guía, el
sistema deberá guardar el cambio al instante, sin botón de guardar y sin preguntar al cerrar. Las
notas son la excepción: se guardan al confirmar su edición, no mientras se escriben (RF-15).
Criterios de aceptación:
- Cuando el usuario modifique un contador y cierre la aplicación de inmediato, el sistema deberá
  conservar ese valor al volver a abrir. `[auto]`
- Si el guardado falla, entonces el sistema deberá devolver el valor al último guardado y avisar de
  que no se pudo guardar, sin mostrar nunca como guardado algo que no lo está. `[manual]`
- Cuando el usuario cierre la aplicación, el sistema no deberá mostrar ningún diálogo de cambios
  sin guardar. `[manual]`

### 4.4 Notas

**RF-14 — Añadir una nota.**
El sistema deberá permitir añadir notas de texto libre a un proyecto, cada una con su fecha y hora
de creación puestas por el sistema, y mostrarlas de la más reciente a la más antigua.
Criterios de aceptación:
- Cuando el usuario guarde una nota con texto, el sistema deberá añadirla al principio de la lista
  con la fecha y la hora del momento de crearla, en formato `dd/mm/aaaa hh:mm`. `[auto]`
- Cuando el usuario intente guardar una nota vacía o solo con espacios, el sistema deberá rechazarla
  y avisar de que falta el texto. `[auto]`
- Cuando el usuario añada una nota y vuelva a abrir el proyecto, el sistema deberá mostrarla en su
  sitio con la misma fecha. `[auto]`

**RF-15 — Editar y borrar notas.**
Criterios de aceptación:
- Cuando el usuario edite el texto de una nota y lo confirme, el sistema deberá guardarlo y mantener
  la fecha de creación original. `[auto]`
- Cuando el usuario cancele la edición de una nota, el sistema deberá restaurar el texto anterior y
  no guardar nada. `[auto]`
- Si el usuario intenta dejar el texto de una nota vacío, entonces el sistema deberá conservar el
  texto anterior y avisar de que falta el texto. `[auto]`
- Cuando el usuario borre una nota y confirme, el sistema deberá eliminarla de la lista y del
  proyecto guardado. `[auto]`
- Cuando el usuario intente borrar una nota y cancele la confirmación, el sistema deberá conservarla. `[auto]`

### 4.5 Deshacer

**RF-16 — Deshacer el último cambio.**
El sistema deberá ofrecer deshacer el último cambio hecho sobre el proyecto abierto, durante los
10 minutos siguientes a hacerlo. Entran los contadores y las notas (alta, edición y borrado). No
entran el nombre, el estado, la página de la guía, la guía, el borrado de un proyecto ni un guardado
fallido.
Criterios de aceptación:
- Cuando el usuario pulse "Deshacer", el sistema deberá revertir el último cambio de contador o de
  nota y guardar el resultado. `[auto]`
- Mientras hayan pasado más de 10 minutos desde el cambio que se puede deshacer, el sistema no
  deberá ofrecer deshacer. `[auto]`
- Cuando el usuario deshaga un cambio, el sistema deberá dejar de ofrecer deshacer: solo hay un
  paso, y el cambio anterior no se puede deshacer. `[auto]`
- El sistema no deberá ofrecer rehacer: el cambio deshecho no se puede volver a aplicar. `[auto]`
- Cuando el usuario deshaga el borrado de una nota, el sistema deberá devolverla con su texto y su
  fecha de creación originales. `[auto]`
- Cuando el usuario deshaga un cambio de contador, el sistema deberá devolver el contador al valor
  anterior al cambio. `[auto]`
- Cuando el usuario cambie de nombre, marque como terminado, adjunte una guía, cambie de página,
  borre un proyecto o sufra un guardado fallido, el sistema no deberá tratar esa acción como
  deshacible, pero tampoco deberá borrar el deshacer pendiente: el deshacer seguirá apuntando al
  último cambio de contador o de nota. `[auto]`
- Cuando el usuario vuelva a la lista o abra otro proyecto, el sistema deberá descartar el deshacer
  pendiente. `[auto]`
- Cuando el usuario cierre la aplicación, el sistema deberá descartar el deshacer pendiente: no se
  guarda en disco. `[auto]`
- Cuando no haya nada que deshacer, el sistema no deberá mostrar el control y no deberá fallar. `[manual]`
- El sistema no deberá tratar la propia acción de deshacer como un cambio deshacible. `[auto]`

### 4.6 Retomar el trabajo

**RF-17 — Retomar un proyecto.**
Cuando el usuario abra un proyecto que ya tenía progreso, el sistema deberá devolverlo al mismo
punto: mismos contadores, misma página de guía y mismas notas.
Criterios de aceptación:
- Cuando el usuario cierre y vuelva a abrir la aplicación, el sistema deberá mostrar la lista de
  proyectos sin haber perdido nada. `[auto]`
- Mientras el usuario no abra un proyecto, el sistema no deberá alterar sus valores guardados. `[auto]`

---

## 5. Requisitos no funcionales

- **RNF-1 — Nada de progreso perdido.** Toda escritura del progreso es completa o inexistente: una
  caída o un cierre forzado no puede dejar un contador a medias. Lo mismo vale para la copia de la
  guía, que no puede quedar a medias. Todo cambio de formato de guardado va con su migración probada
  sobre datos existentes y con copia del archivo anterior. (Constitución §5.)
- **RNF-2 — Inmediatez percibida.** Al pulsar un contador, el número nuevo se ve sin espera
  perceptible. Si el guardado falla, se avisa y se vuelve al último valor guardado; el rendimiento
  no es un criterio de aceptación medible en este MVP. (Ver RF-13.)
- **RNF-3 — Sin red.** La aplicación funciona completa sin conexión: no hay cuentas, ni envío de
  ficheros, ni telemetría. El PDF no sale del equipo. (Constitución §1, §6.)
- **RNF-4 — Sin pérdida por error del usuario.** Borrar un proyecto o una nota exige confirmación;
  deshacer cubre el último cambio (RF-16); reducir un contador por debajo de cero es imposible.
- **RNF-5 — Idioma.** Textos de interfaz y mensajes de usuario en español, claros y sin jerga
  técnica. Código, nombres de fichero y mensajes de commit en inglés. Documentación en español.
  (Constitución §6.)
- **RNF-6 — Todo lo calculable se puede probar sin interfaz ni PDF real.** Las reglas de conteo,
  límites, deshacer y validaciones deben poder comprobarse sin abrir ventanas. (Constitución §3, §4.)
- **RNF-7 — Datos locales, portables y de un solo uso.** El progreso vive en el equipo del usuario,
  en un formato que sobrevive a actualizar la aplicación. La aplicación no depende de ningún
  servicio externo y no admite dos instancias sobre los mismos datos. (Ver RF-7.)

---

## 6. Casos límite

| # | Situación | Comportamiento esperado |
|---|---|---|
| CL-1 | Nombre vacío o solo espacios al crear o renombrar | Se rechaza con mensaje; no se cambia nada |
| CL-2 | Nombre con signos, saltos de línea, emoji o espacios invisibles | Se recortan los extremos; si queda vacío se rechaza; el resto se acepta tal cual |
| CL-3 | Nombre de más de 100 caracteres | No se puede escribir más allá del límite |
| CL-4 | Dos proyectos con el mismo nombre | Se permite, sin aviso; la lista los distingue por su fecha de última modificación |
| CL-5 | Nombre que no cabe en la lista | Se recorta con puntos suspensivos; el completo se ve al pasar el ratón |
| CL-6 | Renombrar a un nombre ya existente | Se permite, igual que al crear |
| CL-7 | Borrar desde la lista un proyecto que se estaba usando | Se borra y desaparece; al abrirlo de nuevo ya no existe |
| CL-8 | Borrar el archivo PDF original | No afecta: la guía está copiada dentro del proyecto |
| CL-9 | La guía copiada desaparece del equipo | Se avisa y el proyecto se comporta como sin guía; se puede añadir otra |
| CL-10 | El PDF se borra o se mueve antes de terminar de copiarlo | Aviso claro; el proyecto se queda sin guía |
| CL-11 | La copia del PDF se interrumpe o se cancela | No queda ningún archivo a medias ni guía asignada |
| CL-12 | El PDF está dañado o protegido con contraseña | Se avisa; el proyecto se abre igual y contadores y notas funcionan |
| CL-13 | El PDF tiene 0 páginas | Se trata como guía ilegible: mismo comportamiento que CL-12 |
| CL-14 | Una sola página del PDF no se puede dibujar | Se avisa en esa página y se puede seguir pasando a las demás |
| CL-15 | PDF enorme o que tarda mucho en prepararse | Se muestra una señal de espera, sin límite de tamaño ni de tiempo, con opción de cancelar |
| CL-16 | Dos proyectos con el mismo PDF | Se copia una vez por proyecto; no se deduplica |
| CL-17 | Reducir un contador en cero | No ocurre nada y no se muestra error |
| CL-18 | Contadores muy altos (p. ej. 100.000 nudos) | Se aceptan y se muestran completos, sin notación científica ni recorte |
| CL-19 | Nota vacía al crear o al editar | Se rechaza; al editar se conserva el texto anterior |
| CL-20 | Nota muy larga | Se acepta y se muestra con desplazamiento, sin truncar el dato guardado |
| CL-21 | Muchísimas notas en un proyecto | Sin límite; se acepta que una lista larga tarde más en mostrarse |
| CL-22 | Reloj del sistema mal puesto o cambio de hora | Se guarda la fecha del sistema y se ordena por ella; las fechas raras son un problema del equipo |
| CL-23 | Editar una nota y arrepentirse | "Cancelar" restaura el texto; cerrar el proyecto descarta la edición no confirmada |
| CL-24 | Cerrar la aplicación justo después de pulsar `+1` | El valor se conserva al reabrir |
| CL-25 | Disco lleno o sin permisos de escritura | Se avisa; no se muestra como guardado lo que no se guardó y el valor vuelve al último guardado |
| CL-26 | La base de datos está dañada o es de una versión más nueva | Se avisa nombrando el archivo y su carpeta; no se destruyen datos |
| CL-27 | No hay ningún proyecto | Se muestra un estado vacío que invita a crear el primero |
| CL-28 | Proyecto terminado | Se abre, cuenta y anota igual que uno en curso; contar no cambia su estado |
| CL-29 | Segundo intento de abrir la aplicación | Se avisa de que ya hay una instancia abierta y no se abre otra ventana |
| CL-30 | Cerrar la aplicación durante una copia de la guía | La copia no queda a medias; el proyecto sigue sin guía |
| CL-31 | El guardado de una nota falla al confirmar | Se avisa; el texto se conserva en el editor y la nota no se da por guardada |

---

## 7. Fuera de alcance

- Interpretar el patrón, leer símbolos de crochet o calcular el avance a partir del PDF.
- Sustituir una guía ya asignada (si eliges mal el PDF, no hay arreglo en este MVP).
- Varios PDFs por proyecto.
- Papelera o recuperación de un proyecto borrado: el borrado es permanente.
- Porcentaje de avance: no hay total con el que comparar, es solo un anotador.
- Subir nudos de golpe (p. ej. «+10») o editar el contador escribiendo un número.
- Cuentas de usuario, sincronización, nube, compartir proyectos, varios dispositivos.
- Varias instancias de la aplicación a la vez sobre los mismos datos.
- Varios proyectos abiertos a la vez en pestañas o ventanas.
- Imprimir, exportar a PDF/CSV o exportar las notas.
- Copias de seguridad automáticas o restauración desde la propia aplicación.
- Recordatorios, notificaciones o avisos por tiempo.
- Buscar o filtrar en la lista de proyectos.
- Estadísticas, gráficas de progreso o tiempos por fila.
- Temas visuales, tamaños de letra configurables, modo oscuro.
- Idiomas distintos del español en la interfaz.
- Uso solo con teclado, atajos de teclado y accesibilidad avanzada.
- Ajuste del PDF al ancho de la ventana, zoom y pantallas de distinta escala.

---

## 8. Criterios de finalización

El MVP está terminado cuando, en una instalación limpia y sin conexión:

1. Se puede crear un proyecto con nombre y, si se quiere, adjuntar un PDF y verlo página a página.
   (RF-1, RF-8, RF-10) `[manual]`
2. Los contadores de filas y nudos suben y bajan de uno en uno, por separado, y no bajan de cero.
   (RF-11, RF-12) `[auto]`
3. Cerrar la aplicación y volver a abrirla devuelve exactamente los contadores, la página de la guía
   y las notas anteriores. (RF-3, RF-13, RF-17) `[auto]`
4. Se puede añadir, editar, cancelar y borrar notas con su fecha. (RF-14, RF-15) `[auto]`
5. Se puede deshacer el último cambio durante los 10 minutos siguientes. (RF-16) `[auto]`
6. Se puede renombrar, marcar como terminado y borrar un proyecto con confirmación. (RF-4, RF-5,
   RF-6) `[manual]`
7. Un PDF dañado produce un mensaje comprensible y deja el proyecto usable. (CL-12) `[manual]`
8. Una segunda instancia de la aplicación no abre una ventana sobre los mismos datos. (RF-7, CL-29)
   `[manual]`
9. `pytest -q` pasa en verde, incluidos los casos de contadores, límites, validaciones y deshacer.
   (Constitución §4) `[auto]`
10. Ningún import de interfaz, PDF o base de datos aparece en la lógica de conteo. (Constitución §3)
    `[auto]`
11. La interfaz está íntegramente en español y no hay ninguna llamada de red. (RNF-3, RNF-5) `[manual]`

---

## 9. Decisiones cerradas para este MVP

- **No se puede sustituir un PDF ya asignado.** Queda para una versión posterior (ver §7). La única
  excepción es que el archivo copiado desaparezca del equipo: entonces el proyecto se comporta como
  si no tuviera guía y se puede añadir otra.
- **No se pide un total de filas ni de nudos y no hay porcentaje de avance.** La aplicación es un
  anotador: cuenta lo hecho, no compara con un objetivo. El porcentaje queda descartado, no
  aparcado.
- **Una sola instancia.** Sustituye la decisión anterior de "gana la última escritura", que se
  descarta por chocar con el principio §5 de la constitución. La constitución no se modifica.
- **El borrado de un proyecto es permanente.** No hay papelera; la confirmación de RF-6 es la única
  red de seguridad. Deshacer no cubre el borrado de un proyecto.
- **Deshacer es de un solo paso, caduca a los 10 minutos y vive en memoria.** Al deshacer una vez,
  no queda nada más que deshacer. Cubre los contadores y las notas, nada más. No hay rehacer. Se
  pierde al cerrar la aplicación, al volver a la lista o al cambiar de proyecto. Los cambios que no
  se pueden deshacer (renombrar, marcar terminado, pasar de página) no lo anulan: el plazo cuenta
  desde el cambio deshacible.
- **Cada acción vive en un sitio.** Renombrar y marcar como terminado, dentro del proyecto abierto;
  borrar un proyecto y elegir cuál abrir, solo desde la lista; añadir la guía, al crear el proyecto
  o desde el proyecto abierto.
- **La guía es opcional** y la lista de proyectos se ordena por última modificación. Abrir un
  proyecto sin tocarlo no reordena la lista.
- **Las notas se guardan al confirmar**, no mientras se escriben; el resto de cambios del proyecto
  se guardan al instante.

## 10. Decisiones delegadas al plan

Esta spec no deja ninguna duda abierta. Quedan dos cosas que decide el plan técnico, no el producto,
y que no pueden contradecir lo anterior:

- **Dónde viven los datos del usuario** (carpeta del sistema, carpeta del ejecutable u otra). RF-7
  necesita ese dato para saber dónde vive el bloqueo de instancia única.
- **Cómo se bloquea la segunda instancia** y con qué, dentro del principio §1 de la constitución:
  nada que no sea la biblioteca estándar de Python.
