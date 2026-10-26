# Revisión de la spec frente al código

> Fecha y hora: 2026-10-25 22:49
> Base: `specs/001-crochet-mvp/spec.md` (rev. 5), `tasks.md` (T01–T09 hechas) y la suite completa.
> Resultado de `pytest -q`: **56 passed in 0.07s**.

## Resumen

Solo existen el dominio y sus tests (T01–T09 de 35). No hay `application/`, `infrastructure/` ni
`presentation/`, así que la mayoría de requisitos funcionales no tiene nada que los cumpla.
Ningún test falla; eso no equivale a cumplir la spec.

---

## 1. Requisitos funcionales

| RF | Qué exige | Test que lo toca | Resultado |
|---|---|---|---|
| **RF-1** Crear proyecto | Nombre 1–100, rechazo de vacío | `test_project_name.py` (recorte, vacío, 100/101, repetidos) | ✅ pasa, pero **solo la validación del nombre**. Crear-y-abrir el proyecto no existe. **Parcial** |
| **RF-2** Ver la lista | Lista con nombre, última modificación, etiqueta "Terminado", orden | ninguno | ❌ **Sin cobertura** |
| **RF-3** Abrir y volver | Abrir con valores guardados, "← Proyectos" | ninguno | ❌ **Sin cobertura** |
| **RF-4** Renombrar | Mismas reglas que crear, nombres repetidos | `test_project_name.py::test_repeated_names_are_allowed` + los de límites | ✅ pasa, **solo reglas de nombre**. El renombrado en sí no existe. **Parcial** |
| **RF-5** Terminado | Alternar estado, etiqueta, contar sin cambiar estado | `test_finished.py` (5 tests) | ✅ pasa en dominio (alternancia y CL-28). Etiqueta y guardado no existen. **Parcial** |
| **RF-6** Borrar proyecto | Borrado con confirmación y cascada | ninguno | ❌ **Sin cobertura** |
| **RF-7** Instancia única | Segundo proceso no abre ventana | ninguno | ❌ **Sin cobertura** |
| **RF-8** Adjuntar guía | Copiar PDF, no sustituir uno existente | ninguno | ❌ **Sin cobertura** |
| **RF-9** Proyecto sin guía | Guía opcional, guía desaparecida = sin guía | ninguno | ❌ **Sin cobertura** |
| **RF-10** Ver y recorrer guía | Página recordada, primera si nunca se abrió, tope en la última | `test_page.py` (6 tests, incluido `test_page_starts_at_one`) | ✅ pasa en dominio. Render del PDF y navegación no existen. **Parcial** |
| **RF-11** Contadores independientes | +1 filas no toca nudos y viceversa | `test_counters.py::test_counters_start_at_zero_and_independent`, `test_decrement_reduces_the_counter` | ✅ pasa en dominio. Persistencia ("al reabrir se ven los mismos valores") no probada. **Parcial** |
| **RF-12** Reducir en uno | Bajar >0 resta uno; en cero no pasa nada ni hay error | `test_counters.py` (`test_decrement_reduces_the_counter`, `test_decrement_at_zero_changes_nothing_and_does_not_raise`, 3 variantes) | ✅ pasa en dominio (CL-17). "Y guardar el cambio" no probado. **Parcial** |
| **RF-13** Guardado inmediato | Guardar al instante; si falla, volver al valor anterior y avisar | ninguno | ❌ **Sin cobertura**. Es el RF más crítico sin nada. |
| **RF-14** Añadir nota | Fecha del sistema, orden reciente→antigua, formato `dd/mm/aaaa hh:mm`, rechazo de vacía | `test_note.py::test_empty_or_blank_text_is_rejected` (3 variantes), `test_note_keeps_body_and_creation_time` | ✅ pasa solo el rechazo y el almacenamiento de la fecha. Orden, formato y persistencia no existen. **Parcial** |
| **RF-15** Editar y borrar notas | Editar conserva fecha; Cancelar restaura; vacío conserva texto anterior | `test_note.py::test_editing_keeps_the_original_creation_time`, `test_editing_to_blank_is_rejected_and_keeps_the_old_text` | ✅ pasa en dominio. Cancelar y borrar son de la UI, no existen. **Parcial** |
| **RF-16** Deshacer | Un paso, 10 min, contadores y notas, sin rehacer, no lo anula un cambio no deshacible, se descarta al cambiar de proyecto | `test_undo.py` (10) + `test_undo_ops.py` (5) | ✅ pasa en dominio, incluida la caducidad con reloj inyectado. Falta conectarlo al guardado y descartarlo al cambiar de proyecto (T23). **Parcial** |
| **RF-17** Retomar proyecto | Contadores, página y notas intactos al reabrir | ninguno | ❌ **Sin cobertura** |

## 2. Requisitos no funcionales

| RNF | Test | Resultado |
|---|---|---|
| RNF-1 atomicidad | ninguno | ❌ |
| RNF-2 inmediatez / fallo de guardado | ninguno | ❌ |
| RNF-3 sin red | no hay código de red en absoluto | ⚠️ trivialmente cierto, sin test |
| RNF-4 sin pérdida por error | suelo en cero y deshacer de un paso probados; borrados y confirmaciones no | ⚠️ parcial |
| RNF-5 idiomas | `test_errors.py::test_error_messages_are_english_only` cubre el dominio; no hay UI que comprobar | ⚠️ parcial |
| RNF-6 todo lo calculable se prueba sin UI ni PDF | sí para nombre, contadores, página, notas y deshacer | ✅ pasa |
| RNF-7 datos locales | no hay persistencia | ❌ |

## 3. Criterios de finalización (§8)

| # | Criterio | Estado |
|---|---|---|
| 1 | Crear proyecto, adjuntar PDF y recorrerlo | ❌ no hay app |
| 2 | Contadores suben/bajan de uno en uno, sin bajar de cero | ⚠️ solo en dominio, sin UI ni guardado |
| 3 | Cerrar y reabrir devuelve todo | ❌ no hay persistencia |
| 4 | Añadir, editar, cancelar y borrar notas | ❌ no hay app |
| 5 | Deshacer el último cambio durante 10 min | ⚠️ solo el mecanismo de dominio |
| 6 | Renombrar, marcar terminado, borrar con confirmación | ❌ |
| 7 | PDF dañado avisa y deja el proyecto usable | ❌ |
| 8 | Segunda instancia no abre ventana | ❌ |
| 9 | `pytest -q` en verde | ✅ **56 passed in 0.07s** |
| 10 | Sin imports de UI/PDF/BD en la lógica de conteo | ✅ `test_project_name.py::test_domain_does_not_import_outer_layers` pasa; verificado además con grep (0 coincidencias) |
| 11 | Interfaz en español, sin red | ❌ no hay interfaz |

## 4. Veredicto

**No, la spec no está cumplida.** Ningún test falla (56/56 en verde), pero eso no equivale a
cumplirla: lo que hay es el núcleo de dominio de 9 tareas de 35. Falta el 74 % del trabajo y, sobre
todo, falta todo lo que el usuario toca.

Reparto honesto de los 17 RF:

- **0 completamente cubiertos.**
- **9 parcialmente cubiertos** (reglas de dominio con test, sin caso de uso, persistencia ni
  pantalla): RF-1, 4, 5, 10, 11, 12, 14, 15, 16.
- **8 sin ninguna cobertura**: RF-2, 3, 6, 7, 8, 9, 13, 17. RF-13 (guardado atómico y vuelta al
  valor anterior) es el más grave porque es el que protege el progreso del usuario.

De los 11 criterios de finalización, 2 pasan (tests en verde y capas limpias), 2 pasan a medias y 7
no.

Siguiente paso natural por dependencia: T10–T18 (infraestructura), luego T19–T24 (aplicación), y
solo entonces la presentación. Hasta que existan `application/` e `infrastructure/`, la spec no
puede aprobarse aunque el dominio esté impecable.

## 5. Límites de esta revisión

- Solo se ejecutó `pytest`; no se valoró la calidad de los criterios marcados `[manual]`.
- El veredicto se basa únicamente en lo que el código y los tests existentes demuestran.
