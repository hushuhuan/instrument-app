# Implementation Plan: 有机合成仪器控制软件（流程与 GUI）

**Branch**: `001-organic-synthesis-control` | **Date**: 2026-05-05 | **Spec**: [spec.md](./spec.md)  
**Input**: `spec.md`；规划补充：**全硬件 Mock / 仿真模式**（FR-018）、**仪器自检**（US4）、六类可编排业务阶段与状态栏。  
**本次增量（/speckit-plan）**: 在 **不改变 Principle IX（Python 实现栈）** 的前提下，规划 **更现代、更美观的 GUI 呈现**（视觉与控件层次），与现有 Domain / HAL / `RunCoordinator` **解耦演进**。

## Summary

交付**单机实验室桌面控制软件**：参数与方法编排（FR-001–FR-005、FR-013）、运行控制（FR-006）、状态栏（FR-011/012）、HAL（FR-007–FR-009）、方法持久化（FR-010）、**仪器自检**（FR-014–FR-017、SC-006）、**Mock 仿真模式**（FR-018、SC-007）。

**GUI 演进（新增）**：在 **Python + Qt（PySide6）** 体系内提升观感与信息层次，**不**引入独立 Web/Electron 前端链（避免宪章例外与部署分裂）。**推荐路径**：在现有 `QtWidgets` 基础上叠加 **Fluent Design 风格组件库（如 PySide6-Fluent-Widgets / QFluentWidgets）** 或 **系统 Fusion + 品牌 QSS + 图标字体**；**进阶备选**：对高动画/仪表盘类界面局部采用 **Qt Quick（QML）** 嵌入 `QQuickWidget`，与 Widgets 共存。详见下文 **「GUI 视觉与框架演进」**。

**自检**：独占式短线性状态机（与工艺 Run 互斥）；主窗 **「自检」** + 结果表；顺序固定；失败短路后续为 `not_run`。

**Mock**：`MockInstrumentHal` 与真机同一 Python 接口；`--mock` / `INSTRUMENT_USE_MOCK=1` 注入；优先级：`CLI > 环境变量 > instrument.json`（建议实现顺序）。

## Technical Context

**Language/Version**: Python **3.11+**（`pyproject.toml` / README）  
**Primary Dependencies**:
- **PySide6**（Qt 6：`QtWidgets`、`QtNetwork`）— **GUI 主栈（必选）**。
- **GUI 美化（规划增量，择一或组合）**：
  - **推荐 A**：**PySide6-Fluent-Widgets**（或等价 Fluent/Qt 6 兼容皮肤库）— 导航帧、卡片、信息栏与 Win11 视觉一致度高。
  - **推荐 B**：**qt-material** / **qdarkstyle** / 自建 **QSS** — 依赖少、风险低，适合快速统一深色/品牌色。
  - **进阶 C**：**Qt Quick / QML** 局部嵌入 — 适合环形进度、大字号工况屏；开发与 Qt Widgets **双栈并列**，成本高于 A/B。
**Storage**: 本地 JSON（`pathlib` / `json`）；自检结果追加日志（FR-017）  
**Testing**: **`pytest`**；默认针对 `MockInstrumentHal`；契约含 schema 与 [mock-mode.md](./contracts/mock-mode.md)  
**Target Platform**: Windows 10/11 实验室单机（其他 Qt6 平台为加分项）  
**Project Type**: desktop-app  
**Performance Goals**: 状态栏 **1 s**；Mock 自检总时长见 SC-006  
**Constraints**: Running 时拒绝自检（FR-016）；互锁在 `RunCoordinator` 层；**Principle IX**：实现语言为 Python；**GUI 库须为 Python 绑定或 QML 资源由 PySide6 加载**。

## GUI 视觉与框架演进（2026-05-05）

| 方案 | 美感 / 现代感 | 工作量 | 风险 | 与宪章 IX |
|------|----------------|--------|------|-----------|
| **A. Fluent 组件库 + PySide6** | 高 | 中（换壳主窗/侧栏/对话框） | 第三方协议与 Qt 版本对齐需验证 | 合规（Python） |
| **B. QSS / qt-material** | 中–高 | 低 | 低 | 合规 |
| **C. QML 局部嵌入** | 高（动效） | 高 | 状态与信号跨 Widget/QML 边界 | 合规 |
| **D. Electron/Tauri + 前端** | 依赖团队前端栈 | 很高 | 进程、升级、工控稳定性 | **需宪章修订例外**（默认不选） |

**决策（本计划）**: 以 **方案 A 或 B 为 v1 美化首选**；若产品要求强动效再评估 **C**。**Simpler path**：先做 **B** 再按需升级 **A**，避免一次替换全部控件类名。

**迁移原则**：
1. **领域与 HAL 不变**；仅 `instrument_app/ui/` 与样式资源变更为主。  
2. **契约不变**（`status-bar-state.schema.json`、`workflow-step-mapping.md` 语义不变；文案可更美观但不改六类阶段名）。  
3. **验证**：`pytest` 全绿 + Mock 下手工扫关键屏（参数、方法编辑、自检、设备调试）。

## Constitution Check

- **Python stack（Principle IX）**：GUI 美化仍落在 **Python + PySide6（+ 可选 QML 资源）**；无未备案的他语主体实现。  
- **Traceability**：自检与 Mock 已对齐 spec 与契约；本增量在 plan/research 立项，后续应增 `tasks.md` 专项（皮肤/主窗框架）。  
- **Simplicity**：优先 QSS/单库换肤；避免同时 A+B+C 全上。  
- **Tradeoffs（Principle II）**：已在表中列出；不默认采用跨进程 Web 壳。  
- **Goal-Driven**：验收 = 现有自动测试 + 视觉回归检查清单（可附截图基准）。

## Project Structure

### Documentation (this feature)

```text
specs/001-organic-synthesis-control/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── status-bar-state.schema.json
│   ├── workflow-step-mapping.md
│   ├── self-test-report.schema.json
│   └── mock-mode.md
├── checklists/
└── spec.md
```

### Source Code（当前落实）

```text
src/instrument_app/
├── app/
├── ui/
├── domain/
│   └── selftest/
├── hal/
│   ├── interfaces/
│   ├── mock/
│   └── real/
├── persistence/
└── logging/
tests/
```

**Structure Decision**: 单体 Python 包 + 按层分目录；GUI 美化任务集中在 `ui/` 与静态资源（`resources/` 若新增 `*.qss`、`*.svg`）。

### Source Code（仓库内遗留 C++ 树，可选维护）

CMake/Qt C++ 布局与 **Principle IX 主交付** 并行存在时，须在 README/plan 标明 **主交付为 Python**；C++ 树退役或冻结需单独变更任务。

## 仪器自检（设计）

### 固定顺序（FR-015）

| # | `SelfTestStepId` | 行为摘要 |
|---|------------------|----------|
| 1 | `Network` | TCP connect 可配 `host:port`（~3 s）；未配置则弱检本机解析 |
| 2 | `DiskSpace` | `shutil.disk_usage`；可用 ≥ `minFreeBytes`（缺省 1 GiB） |
| 3 | `PumpInit` | `HAL.init_pumps()` |
| 4 | `RotaryValveInit` | `HAL.init_rotary_valve()` |
| 5 | `StepperHome` | `HAL.home_stepper()` |
| 6 | `ChillerComm` | `HAL.chiller_handshake()` |

失败策略：步骤 *i* 失败 → 后续标记 `not_run`；禁止显示为 Pass。与 Run **互斥**（FR-016）。

### UI

- 主界面 **自检**；对话框表格：步骤名、状态、详情、耗时；结果 JSON 见 `self-test-report.schema.json`。

### 与 HAL 边界

网络/磁盘在应用核心；泵/阀/电机/冷机经 HAL，便于 Mock。

## 全硬件 Mock（FR-018）

- 进程内 `MockInstrumentHal`；主窗 **仿真模式** 角标；`timeScale` 压缩阶段耗时。  
- 详见 [contracts/mock-mode.md](./contracts/mock-mode.md)。

## Phase 0 / Phase 1（Speckit 流程对齐）

- **Phase 0**：本增量结论写入 [research.md](./research.md) **R9**。  
- **Phase 1**：`data-model.md` / `contracts/` / `quickstart.md` **无破坏性变更**；若引入新资源目录，在 quickstart 中增加「主题/Fluent 依赖安装」一行即可。  
- **tasks.md**：需后续 `/speckit.tasks` 生成「UI-美化」分解任务（可选独立 US 或 Phase 10）。

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 可选 QML 嵌入 | 仅当单 Widget 无法满足动效 KPI | 全 QML 重写成本高 |

**默认**：不填本表；若仅采用 QSS/Fluent 库换肤，**无违宪项**，本表可空。
