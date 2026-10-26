# Revisión de la spec 001 — 2026-10-26

> Comando de referencia: `.\.venv\Scripts\python.exe -m pytest -q` → **276 passed**.
> Cada RF se ha ejecutado además por separado (`pytest -q <archivos> -k "<filtro>"`), con el
> número de tests que se indica. Las selecciones de dos RF pueden compartir algún test.

## 1. Requisitos funcionales

| RF | Qué lo cubre (archivo · casos) | Ejecución |
|---|---|---|
| **RF-1** Crear proyecto | `domain/test_project_name.py` (recorte, vacío, 100/101, repetidos) · `application/test_projects.py::test_created_project_starts_empty`, `::test_create_rejects_names_the_domain_refuses[4]`, `::test_duplicate_names_are_allowed` · `infrastructure/test_repository.py::test_creating_a_project_stores_it` · `presentation/test_list.py::test_creating_a_project_opens_it`, `::test_creating_without_a_name_warns_and_creates_nothing[3]`, `::test_cancelling_creates_nothing`, `::test_a_repeated_name_is_accepted` | **10 passed** |
| **RF-2** Ver la lista | `infrastructure/test_repository.py` (orden por `updated_at`, desempate por id) · `presentation/test_list.py::test_empty_state_is_shown_without_projects`, `::test_projects_are_listed_newest_change_first`, `::test_a_row_shows_when_it_changed_last`, `::test_a_long_name_is_elided_and_kept_in_the_tooltip` · `presentation/test_list_actions.py::test_a_finished_project_is_labelled_and_stays_in_the_list` · `application/test_projects.py::test_open_does_not_reorder_the_list` | **26 passed** |
| **RF-3** Abrir y volver | `application/test_projects.py::test_open_returns_the_saved_progress`, `::test_open_a_deleted_project_returns_none` · `infrastructure/test_repository.py::test_opening_a_project_does_not_reorder_the_list`, `::test_every_change_reads_back_the_same_after_reopening` · `presentation/test_navigation.py` (6) · `presentation/test_list_actions.py::test_opening_from_the_list_does_not_reorder_it` | **15 passed** |
| **RF-4** Renombrar | `domain/test_project_name.py` (mismas reglas que al crear) · `application/test_projects.py::test_rename_is_saved_and_survives_reopening`, `::test_rename_to_a_blank_name_keeps_the_previous_one`, `::test_rename_restores_the_old_name_when_saving_fails` · `infrastructure/test_repository.py::test_renaming_persists_and_bumps_updated_at` · `presentation/test_project_actions.py` (nombre y renombrado, 6) | **28 passed** |
| **RF-5** Terminado | `domain/test_finished.py` (5) · `application/test_projects.py::test_finished_state_toggles_and_is_saved`, `::test_finished_state_is_kept_when_saving_fails` · `infrastructure/test_repository.py::test_finishing_a_project_persists_both_ways` · `presentation/test_project_actions.py::test_marking_finished_shows_the_label`, `::test_unmarking_hides_the_label`, `::test_a_finished_project_still_counts` (CL-28) · `presentation/test_list_actions.py::test_a_finished_project_can_still_be_opened` | **15 passed** |
| **RF-6** Borrar | `application/test_projects.py::test_delete_removes_the_project_and_its_notes`, `::test_delete_of_a_missing_project_is_silent` · `infrastructure/test_delete_repo.py` (5, incluye borrado del PDF copiado) · `infrastructure/test_atomicity.py::test_a_failed_delete_keeps_the_project_its_notes_and_its_guide` · `presentation/test_list_actions.py::test_deleting_asks_with_the_project_name`, `::test_cancelling_keeps_the_project`, `::test_confirming_removes_it_from_the_list`, `::test_confirming_removes_its_notes` | **15 passed** |
| **RF-7** Instancia única | `infrastructure/test_single_instance.py` (5: primero obtiene el bloqueo, segundo no, liberar permite volver, `app.lock` en la carpeta de datos) · `test_entrypoint.py::test_a_second_instance_warns_and_exits_with_0`, `::test_without_arguments_it_starts_and_closes_normally` | **6 passed** |
| **RF-8** Adjuntar guía | `infrastructure/test_guide_store.py` (9: copia, original borrado, nombres distintos, no-PDF, 0 páginas, copia interrumpida) · `application/test_guide.py::test_attaching_a_guide_copies_it_and_remembers_its_name`, `::test_a_project_with_a_guide_gets_no_second_one`, `::test_an_unreadable_file_leaves_the_project_without_a_guide`, `::test_a_guide_that_cannot_be_saved_is_not_assigned` · `presentation/test_guide_view.py::test_attaching_a_pdf_shows_it_without_restarting`, `::test_cancelling_the_file_dialog_changes_nothing`, `::test_a_file_that_is_not_a_pdf_warns_and_stays_without_guide`, `::test_a_project_with_a_guide_does_not_offer_another` | **12 passed** |
| **RF-9** Proyecto sin guía | `presentation/test_guide_view.py::test_without_a_guide_it_says_so_and_offers_one`, `::test_broken_stored_file_behaves_as_no_guide`, `::test_a_missing_stored_file_behaves_as_no_guide` · `infrastructure/test_guide_store.py::test_a_missing_guide_is_reported_as_no_guide` · `application/test_guide.py::test_an_unreadable_file_leaves_the_project_without_a_guide` | **6 passed** |
| **RF-10** Ver y recorrer | `domain/test_page.py` (6) · `application/test_guide.py::test_the_new_page_is_saved_at_once`, `::test_the_first_page_cannot_go_back`, `::test_the_last_page_cannot_go_forward`, `::test_a_page_that_cannot_be_saved_goes_back` · `infrastructure/test_repository.py::test_the_guide_page_persists` · `presentation/test_guide_view.py` (página guardada, primera, siguiente/anterior guardadas, última, página fuera de rango, página rota) | **17 passed** |
| **RF-11** Contadores | `domain/test_counters.py` (independencia, suelo, 100 000+) · `application/test_counters.py` (13) · `infrastructure/test_repository.py::test_counter_changes_persist_and_do_not_touch_the_other_counter` · `presentation/test_counters_view.py` (10, incluido `100 001` completo y reabrir) | **31 passed** |
| **RF-12** Reducir | `domain/test_counters.py::test_decrement_at_zero_changes_nothing_and_does_not_raise[3]` · `application/test_counters.py::test_remove_takes_one_off_a_positive_counter`, `::test_removing_at_zero_changes_and_saves_nothing[2]` · `presentation/test_counters_view.py::test_decreasing_is_disabled_at_zero`, `::test_decreasing_works_above_zero`, `::test_decreasing_back_to_zero_disables_the_button` | **15 passed** |
| **RF-13** Guardado inmediato | `infrastructure/test_atomicity.py` (3: commit fallido no deja nada a medias) · `application/test_counters.py::test_every_count_is_saved_at_once`, `::test_a_failed_save_puts_the_counter_back[4]` · `application/test_projects.py::test_rename_restores_the_old_name_when_saving_fails`, `::test_finished_state_is_kept_when_saving_fails` · `presentation/test_counters_view.py::test_a_failed_save_warns_and_keeps_the_previous_value`, `::test_adding_a_row_counts_and_saves` · `presentation/test_project_actions.py::test_a_failed_rename_warns_and_keeps_the_previous_name`, `::test_a_failed_toggle_warns_and_keeps_the_state` | **25 passed** |
| **RF-14** Añadir nota | `domain/test_note.py` (vacío rechazado, multilínea, fecha) · `application/test_notes.py::test_a_note_is_stored_with_its_date`, `::test_newest_note_comes_first`, `::test_a_blank_note_is_rejected[3]`, `::test_a_note_that_cannot_be_saved_is_not_stored` · `infrastructure/test_notes_repo.py` (7) · `presentation/test_notes_panel.py::test_a_new_note_appears_with_its_date`, `::test_the_newest_note_goes_first`, `::test_adding_clears_the_draft`, `::test_a_blank_note_warns_and_is_not_stored[3]` | **41 passed** |
| **RF-15** Editar y borrar notas | `domain/test_note.py::test_editing_keeps_the_original_creation_time`, `::test_editing_to_blank_is_rejected_and_keeps_the_old_text` · `application/test_notes.py::test_editing_keeps_the_creation_date`, `::test_a_failed_edit_keeps_the_previous_text`, `::test_deleting_removes_the_note`, `::test_a_failed_delete_keeps_the_note` · `infrastructure/test_notes_repo.py::test_editing_a_note_keeps_its_creation_time`, `::test_deleting_a_note_leaves_the_others` · `presentation/test_notes_panel.py::test_cancelling_restores_the_previous_text` (CL-23), `::test_a_blank_edit_warns_and_keeps_the_text`, `::test_deleting_asks_and_removes_the_note`, `::test_cancelling_the_delete_keeps_the_note` | **17 passed** |
| **RF-16** Deshacer | `domain/test_undo.py` (10: un solo paso, ventana de 10 min, sin rehacer) · `domain/test_undo_ops.py` (5) · `application/test_undo.py` (12) · `presentation/test_undo_banner.py` (15: aparece, caduca, desaparece al deshacer, no lo crean renombrar/terminar, se descarta al volver a la lista o abrir otro proyecto) | **42 passed** |
| **RF-17** Retomar | `infrastructure/test_repository.py::test_every_change_reads_back_the_same_after_reopening`, `::test_created_projects_persist_across_repositories` · `infrastructure/test_migrations.py` (7, migración con datos) · `application/test_projects.py::test_open_returns_the_saved_progress` · `presentation/test_counters_view.py::test_reopening_shows_the_saved_values` · `presentation/test_notes_panel.py::test_notes_are_still_there_when_the_project_is_reopened` · `presentation/test_guide_view.py::test_it_opens_where_the_user_left` | **18 passed** |

## 2. Requisitos no funcionales

| RNF | Cobertura | Estado |
|---|---|---|
| **RNF-1** Nada de progreso perdido | `test_atomicity.py` (commit fallido), `test_guide_store.py::test_an_interrupted_copy_leaves_no_half_file`, `test_migrations.py` (copia `.bak`, rollback, versión más nueva rechazada) | Cumplido |
| **RNF-2** Inmediatez percibida | `test_counters_view.py` (el número cambia al pulsar) y `test_a_failed_save_warns_and_keeps_the_previous_value` | Cumplido; el rendimiento no es medible por spec |
| **RNF-3** Sin red | grep de `socket|http|urllib|requests|QNetwork` en `crochet_tracker/`: **cero coincidencias** | Cumplido |
| **RNF-4** Sin pérdida por error del usuario | confirmación al borrar proyecto (`test_list_actions.py`) y nota (`test_notes_panel.py`), deshacer (42 tests), suelo en cero | Cumplido |
| **RNF-5** Idioma | `test_navigation.py::test_every_visible_text_is_spanish` (cada texto visible debe estar declarado en `strings.py`), mensajes de error del dominio en inglés (`test_errors.py`) | Cumplido |
| **RNF-6** Todo lo calculable sin interfaz ni PDF real | 107 tests sin Qt (`tests/domain`, `tests/application`), más los de infraestructura sobre `tmp_path` | Cumplido |
| **RNF-7** Datos locales y una sola instancia | `test_paths.py` (override y carpeta por defecto), `test_single_instance.py` | Cumplido |

## 3. Criterios de finalización (§8)

| # | Criterio | Evidencia | Estado |
|---|---|---|---|
| 1 | Crear con nombre, adjuntar PDF y verlo página a página | RF-1, RF-8, RF-10 en verde; verificado además con el `.exe` arrancado | Cumple en automático; falta la pasada manual |
| 2 | Contadores ±1 por separado, sin bajar de cero | RF-11, RF-12 (46 tests) | **Cumplido** |
| 3 | Cerrar y reabrir devuelve contadores, página y notas | RF-13, RF-17 + `test_every_change_reads_back_the_same_after_reopening` | **Cumplido** |
| 4 | Añadir, editar, cancelar y borrar notas con fecha | RF-14, RF-15 (58 tests) | **Cumplido** |
| 5 | Deshacer el último cambio durante 10 minutos | RF-16 (42 tests, con reloj inyectado) | **Cumplido** |
| 6 | Renombrar, terminar y borrar con confirmación | RF-4, RF-5, RF-6 (58 tests; el diálogo se sustituye en los tests) | Cumple en automático; falta la pasada manual |
| 7 | PDF dañado: mensaje comprensible y proyecto usable | `test_guide_store.py::test_a_file_that_is_not_a_pdf_is_rejected`, `test_guide_view.py::test_broken_stored_file_behaves_as_no_guide`, `test_a_file_that_is_not_a_pdf_warns_and_stays_without_guide` | Cumple en automático; falta la pasada manual |
| 8 | Segunda instancia no abre otra ventana | `test_single_instance.py` (5) + `test_entrypoint.py::test_a_second_instance_warns_and_exits_with_0` | Cumple en automático con doble; **no probado con dos procesos reales** |
| 9 | `pytest -q` en verde | 276 passed | **Cumplido** |
| 10 | Ningún import de interfaz, PDF o base de datos en la lógica | `test_domain_does_not_import_outer_layers`, `test_application_does_not_import_outer_layers` + grep manual: cero coincidencias | **Cumplido** |
| 11 | Interfaz en español y sin red | guard de textos + grep de red | Cumplido en lo automático; falta la pasada manual de toda la interfaz |

## 4. Veredicto

**La spec está cumplida en todo lo comprobable automáticamente**: los 17 RF tienen tests propios
y pasan, los 7 RNF están cubiertos y los 11 criterios de §8 se sostienen con evidencia real
(276 tests en verde, `.exe` construido y arrancado, cero imports de red y cero imports de capas
externas en `domain/` y `application/`).

Queda pendiente lo que la propia spec marca `[manual]` y no se puede sustituir con tests:

- la pasada a mano de los 11 criterios en un equipo sin Python (T35);
- comprobar con dos procesos reales el aviso de instancia única (en un proceso no se puede simular);
- el aspecto real de los diálogos y del visor del PDF en pantalla.

Ningún requisito está sin cubrir. Ningún test falla. La deuda es de verificación manual, no de
implementación.
