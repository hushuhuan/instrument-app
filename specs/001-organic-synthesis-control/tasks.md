# Tasks: Organic synthesis instrument control (GUI + HAL + mock)

**Input**: `specs/001-organic-synthesis-control` ? GUI workflow, HAL/Mock split, US3 / FR-007.

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [data-model.md](./data-model.md), [research.md](./research.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

**Tests**: Prefer TDD where practical; pytest for automation. See [quickstart.md](./quickstart.md) for SC-002/005/008 and JSON fixtures.

**Organization**: Phases follow [US5] after US1; US2 after US5; **US3** after Foundational + HAL refactor.

**Stack (Principle IX)**: **Python 3.11+** + **PySide6** per [plan.md](./plan.md).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: May run in parallel when dependencies allow.
- **[Story]**: US1?US5 / US3 tags; **[US3]** matches spec User Story 3 (not US6).

## Path Conventions

- `pyproject.toml`, `src/instrument_app/`, `tests/`

---

## Phase 1: Setup??????

**Purpose**: Python ??????????

- [x] T001 Create repository layout per plan: `src/instrument_app/app/`, `src/instrument_app/ui/`, `src/instrument_app/domain/`, `src/instrument_app/domain/selftest/`, `src/instrument_app/hal/interfaces/`, `src/instrument_app/hal/mock/`, `src/instrument_app/hal/real/`, `src/instrument_app/persistence/`, `src/instrument_app/logging/`, `tests/` at repo root
- [x] T002 Add root `pyproject.toml` with `requires-python >=3.11`, dependency `PySide6`, console script `instrument-app` ? `instrument_app.app.main:main`
- [x] T003 [P] Add `src/instrument_app/app/main.py` parsing `--mock` and env `INSTRUMENT_USE_MOCK` (priority: CLI > env > future `instrument.json`) per [contracts/mock-mode.md](./contracts/mock-mode.md)
- [x] T004 [P] Extend `.gitignore` for `.venv/`, `__pycache__/`, `*.egg-info/`, `.pytest_cache/` plus existing build/Qt patterns
- [x] T005 Update `README.md` at repo root with pointer to `specs/001-organic-synthesis-control/quickstart.md` and Python install/run

**Checkpoint**: `pip install -e ".[dev]"` succeeds; imports `instrument_app` OK.

---

## Phase 2: Foundational??????????

**Purpose**: Domain ???Mock HAL?`RunCoordinator`???+????

**?? CRITICAL**: ?????????????

- [x] T006 Define `ApplicationRunMode` and `AppConfig` in `src/instrument_app/domain/app_config.py` (load order per [data-model.md](./data-model.md))
- [x] T007 Define `Recipe`, `RecipeStep`, `BusinessPhase`, `ProcessParameters` in `src/instrument_app/domain/recipe_models.py` and run enums/state in `src/instrument_app/domain/run_models.py` per [data-model.md](./data-model.md)
- [x] T008 Declare `InstrumentHal` protocol in `src/instrument_app/hal/interfaces/instrument_hal.py` (pump, rotary valve, stepper home, chiller as methods)
- [x] T009 Implement `MockInstrumentHal` in `src/instrument_app/hal/mock/mock_instrument_hal.py` with `mock_time_scale` delay simulation and no real I/O
- [x] T010 Implement `ApplicationContext` in `src/instrument_app/app/application_context.py` selecting Mock vs Real HAL from `AppConfig` (Real stub until US3)
- [x] T011 Implement `RunCoordinator` in `src/instrument_app/domain/run_coordinator.py` (PySide6 `QObject` + signals; idle/running; `abort`; hooks for future self-test)
- [x] T012 Implement minimal `phase_script_router.py` in `src/instrument_app/domain/phase_script_router.py` executing **`??`** phase via `InstrumentHal` timing (Mock success path)
- [x] T013 Create `MainWindow` shell in `src/instrument_app/ui/main_window.py` with **????** banner when Mock (FR-018)
- [x] T014 Implement `StatusBarPresenter` + 1s `QTimer` in `src/instrument_app/ui/status_bar_presenter.py` consuming `ambient_reading()` from HAL
- [x] T015 Wire `MainWindow` status bar to `RunCoordinator` + HAL for FR-011 fields

**Checkpoint**: `instrument-app --mock` launches main window + ????; status bar ticks.

---

## Phase 3: User Story 1 ? ??????? (Priority: P1) ?? MVP

**Goal**: FR-001?FR-003

**Independent Test**: ?????????

- [x] T016 [US1] Implement `parameter_validation.py` in `src/instrument_app/domain/parameter_validation.py` (ranges, required fields per FR-002)
- [x] T017 [US1] `ProcessParameters` in `src/instrument_app/domain/recipe_models.py` mirroring FR-001 fields
- [x] T018 [US1] Create `ParametersForm` in `src/instrument_app/ui/parameters_form.py` with Qt widgets for all FR-001 fields + validation feedback
- [x] T019 [US1] Connect `ParametersForm` to validation; block ???? when invalid (`MainWindow` ready label)
- [x] T020 [US1] Add `ParametersSummaryWidget` in `src/instrument_app/ui/parameters_summary_widget.py` for FR-003

**Checkpoint**: US1 ??????????

---

## Phase 4: User Story 5 ? ??????????? Mock?(Priority: P2)

**Goal**: FR-019

**Independent Test**: `--mock` ?????? `Completed`

- [x] T021 [US5] Add `ReactionTaskDialog` in `src/instrument_app/ui/reaction_task_dialog.py`
- [x] T022 [US5] Implement `recipe_from_reaction_task` in `src/instrument_app/domain/recipe_factory.py`
- [x] T023 [US5] On **??**, call `RunCoordinator.start_run` only if coordinator idle; else `QMessageBox`
- [x] T024 [US5] Add toolbar **??????** in `src/instrument_app/ui/main_window.py`
- [x] T025 [US5] `device_args` on `RecipeStep` for reaction (temperature, stir speed)
- [x] T026 [US5] Status bar shows **??** + ETA during run

**Checkpoint**: Mock ? SC-008 ????

---

## Phase 5: User Story 2 ? ?????????? (Priority: P2)

**Goal**: FR-004, FR-005, FR-013, FR-006

**Independent Test**: Mock ??????? SC-002 ??

- [x] T027 [US2] Implement `RecipeStepsModel` (`QAbstractListModel`) in `src/instrument_app/ui/recipe_steps_model.py` for `steps[]` CRUD + reorder
- [x] T028 [US2] Create `RecipeEditorWidget` in `src/instrument_app/ui/recipe_editor_widget.py` (FR-013)
- [x] T029 [US2] Extend `phase_script_router.py` for all `BusinessPhase` values per [plan.md](./plan.md)
- [x] T030 [US2] Wire **????** control: build `Recipe` from editor + `ProcessParameters`, `start_run`
- [x] T031 [US2] Add `RunProgressWidget` in `src/instrument_app/ui/run_progress_widget.py` (FR-005, FR-006)
- [x] T032 [US2] Persist/load Recipe JSON in `src/instrument_app/persistence/recipe_repository.py` (FR-010)

**Checkpoint**: US2 ????????

---

## Phase 6: User Story 4 ? ???? (Priority: P2)

**Goal**: FR-014?FR-017, SC-006

**Independent Test**: Mock ????? quickstart

- [x] T033 [US4] Define `SelfTestStepId` and `SelfTestOrchestrator` in `src/instrument_app/domain/selftest/self_test_orchestrator.py` per [plan.md](./plan.md)
- [x] T034 [US4] Network check in `src/instrument_app/domain/selftest/network_check.py`
- [x] T035 [US4] Disk check in `src/instrument_app/domain/selftest/disk_check.py`
- [x] T036 [US4] Wire steps 3?6 to `InstrumentHal` in orchestrator
- [x] T037 [US4] `SelfTestDialog` in `src/instrument_app/ui/self_test_dialog.py` + JSON per [contracts/self-test-report.schema.json](./contracts/self-test-report.schema.json)
- [x] T038 [US4] Add **??** to `MainWindow`; FR-016 with `RunCoordinator`
- [x] T039 [US4] Append self-test summary to `logs/selftest.log` via `src/instrument_app/logging/log.py` (FR-017)

**Checkpoint**: SC-006 ????????

---

## Phase 7: User Story 3 ? HAL ??????? (Priority: P3)

**Goal**: FR-007?FR-009

- [x] T040 [US3] Split mock into modules under `src/instrument_app/hal/mock/` (pump, valve, stepper, chiller, ?)
- [x] T041 [US3] **????** API guarded by env or `INSTRUMENT_TEST_HOOKS`
- [x] T042 [US3] Harden `src/instrument_app/hal/real/real_instrument_hal.py` until hardware known
- [x] T043 [US3] Device health summary for FR-008 in UI
- [x] T044 [US3] Alarm log FR-009 in `src/instrument_app/logging/alarm_log.py`

**Checkpoint**: Mock ??????? SC-004 ??

---

## Phase 8: User Story 3???? ??????? / ??? / ??? (Priority: P2)

**Goal**: ????? **????** ???? **???**?**???**?**????????/???????** ????????????????/??/??????? **FR-007**??????? US3???????????**?**???????????? **Run/????**?? FR-016 ???**???????**?????????????????

**Independent Test**: `--mock` ?????????????????? UI ?????? **???????** ???????/?/????? **??** ??????????????????? `RealInstrumentHal` ??????????

- [x] T049 [US3] Extend `InstrumentHal` in `src/instrument_app/hal/interfaces/instrument_hal.py` with **debug/manual** methods (v1 ???)??? `debug_pump_command(...)`???/??/??????`debug_rotary_valve_position(...)`????????`debug_chiller_setpoint/readback(...)`??????????????? docstring ??????? [plan.md](./plan.md) ???????
- [x] T050 [US3] Implement mock implementations in `src/instrument_app/hal/mock/mock_instrument_hal.py`??? + ?????/?????? T041 ????
- [x] T051 [US3] Extend `src/instrument_app/hal/real/real_instrument_hal.py` ?????? `not_implemented` / ?????? T042 ????
- [x] T052 [US3] Create `DebugDevicePage` (`QWidget`) in `src/instrument_app/ui/debug_device_page.py`??? UI???????????????????/ SpinBox ?? T049 API ??
- [x] T053 [US3] Wire `DebugDevicePage` to `ApplicationContext` HAL?? `not RunCoordinator.is_idle()` ? self-test ??? **??** ??? `QToolTip`/?????????????????
- [x] T054 [US3] Add **????????**?? **?? ? ????**?? `src/instrument_app/ui/main_window.py` ??????`QDockWidget`?`QDialog` ? `QStackedWidget` ?????????Mock ??? **????** ??
- [x] T055 [P] [US3] Optional: append one-line audit for each debug command in `src/instrument_app/logging/debug_device.py` ??? `logging/` ????

**Checkpoint**: Mock ????????????? ? ?/?/????????????????????

---

## Phase 9: Polish & Cross-Cutting

**Purpose**: ??????????

- [x] T056 [P] Add dev action: export status snapshot JSON vs [contracts/status-bar-state.schema.json](./contracts/status-bar-state.schema.json) in `src/instrument_app/ui/main_window.py`
- [x] T057 [P] Align `quickstart.md` with **???** ? FR-019 ??
- [x] T058 Run manual checklist against `specs/001-organic-synthesis-control/checklists/requirements.md`
- [x] T059 Review [contracts/workflow-step-mapping.md](./contracts/workflow-step-mapping.md) still matches UI labels

---

## Phase 10: GUI polish (plan path B ? Fusion + QSS)

**Purpose**: Lab-friendly global theme without Web/Electron; qt-material?class polish via bundled QSS.

- [x] T060 Add `src/instrument_app/ui/app_theme.py` and `src/instrument_app/ui/styles/app.qss` (Fusion + stylesheet)
- [x] T061 Call `apply_app_theme` from `src/instrument_app/app/main.py` after `QApplication` creation
- [x] T062 Add `tests/test_app_theme.py`; register `package-data` for `styles/*.qss` in `pyproject.toml`

---

## Dependencies & Execution Order

### Phase Dependencies

1. **Setup (1)** ? **Foundational (2)** ? **US1 (3)** ? **US5 (4)** ? **US2 (5)** / **US4 (6)** / **??? (8)** ??? **(2)**?**??? (8)** ??? **T009?T011** ???? **US2** ???????????
2. **US3 (7)** ?? HAL?**Phase 8** ?? **T040** ????????? monolithic mock ???? API??????
3. **Polish (9)** ??

### User Story Dependencies

- **??? (T049?T055)** ?? **Foundational**???? **`InstrumentHal`** ???? **RunCoordinator** / ????????
- **US5** ?? **US1** ? **Foundational**
- **US2** ?? **US5** ??????

### MVP Scope

- ? **?????**: Phase 1?3 + Phase 4 (US5)
- **?????**?? MVP ???? **Phase 8?????** ??????????????????? **US2 ???**

### Parallel Opportunities

- T003/T004?T034/T035?T040 ? **T050**?mock ???????????? **[P]**?T055/T056/T057 **[P]**

---

## Parallel Example

```text
# After InstrumentHal debug API frozen:
- T050 mock methods in mock_instrument_hal.py
- T052 DebugDevicePage layout-only stub in debug_device_page.py
```

---

## Implementation Strategy

1. Phase 1?2?`--mock` ??
2. US1 ? US5
3. **Phase 8 ???**???/Mock ???
4. US2 / US4 / US3?T040?T044?
5. Polish

## Notes

- ????????`step ? verify` ? [constitution Principle VIII](.specify/memory/constitution.md)
- **Constitution**: Principle IX ? Python?Mock ???FR-018?
- **Spec ????**???????????? FR?????? `/speckit-specify` ?? **FR-0xx???????** ? SC ????
