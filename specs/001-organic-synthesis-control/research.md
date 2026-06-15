# Phase 0 Research: 有机合成仪器控制软件

**Feature**: `001-organic-synthesis-control`  
**Date**: 2026-05-05

## R1 — 桌面 GUI 技术选型

**Decision**: 使用 **Qt 6（Widgets）** 作为 GUI 与主程序框架。

**Rationale**: 仪器控制常见组合；成熟的主窗/停靠/状态栏组件；国际化与样式表；与 C++ 单体二进制部署一致；工业场景资料多。

**Alternatives considered**:

- **.NET WPF**：开发效率高但与仓库名 CPP 及跨组件 C++ HAL 混用成本高。
- **wxWidgets**：许可友好但生态与厂商示例相对少。
- **Electron + 原生插件**：JS 与实时设备控制分层复杂，违背 Simplicity First。

## R2 — 硬件抽象形态

**Decision**: **HAL 接口层**（纯虚接口 + 模拟实现 + 日后按总线拆分的适配）。按能力分泵、多路阀、开关阀、电机、电磁铁；上位命令统一经 **Run Orchestrator** 序列化。

**Rationale**: 规格要求统一接口（FR-007）；便于无硬件测试（FR-008/009）；不把 Modbus/串口细节泄漏进 domain。

**Alternatives considered**:

- **每设备裸驱动直连 UI**：最短路径但违反可测性与 Surgical 边界。
- **ROS2 / microservices**：远超单机仪器规模。

## R3 — 状态栏刷新与单位

**Decision**: **1 s `QTimer`**；温湿度一次采集快照在 tick 内更新 ViewModel；**温度内部以 ℃ 存储**，UI 根据用户选择显示 ℃/℉；**湿度仅 %RH**。

**Rationale**: 与规划输入一致；1 s 满足环境量缓变与 CPU 占用平衡。

**Alternatives considered**:

- **500 ms**：略增负载，环境量无须更高频。
- **传感器侧切换 ℉**：增加固件耦合，软件换算更简单。

## R4 — 整体剩余时间（ETA）

**Decision**: **v1 确定性 ETA**：`ETA = Σ(剩余步骤 planDuration)`；反应段落使用方法内 **反应时间** 等参数；缺失 planDuration 的步骤使用配置默认或由方法编辑器强制填写（计划在 data-model 标注）。

**Rationale**: 可验证、可解释；不依赖历史数据。

**Alternatives considered**:

- **仅显示百分比/步号**：不满足本次规划“整体剩余时间”。
- **学习式预测**：超出规格与 Simplicity。

## R5 — 业务阶段与状态栏对齐（已演进）

**Superseded by R6**：早期曾将多个子步映射为「反应」展示；现 **用户可见步骤仅有六类 `businessPhase`**，状态栏与之一一对应，见当前 `workflow-step-mapping.md`。

## R6 — 可重复、任意顺序的业务序列

**Decision**: `Recipe.steps[]` **有序列表**；元素仅为六类 `businessPhase`；**允许重复**；**顺序完全用户定义**；运行器 **线性**执行。v1 **不**实现化学合理性 DAG 校验，**仅**硬件/安全互锁拦截。

**Rationale**: 用户明确要求「每步可多次、顺序随意」；化学约束应由实验 SOP 与操作员负责，避免首版范围膨胀。

**Alternatives considered**:

- **固定Recipe模板 + 允许微调**：违背「随意调整」。
- **内置合法转移图**：维护成本高，留待未来若法规/客户要求。

## R7 — 仪器自检流程

**Decision**: **固定六步**线性自检（网络→磁盘→泵→旋转阀→步进回原→冷热水机）；**与工艺 Run 互斥**；失败 **短路**后续为 `not_run`；UI **单按钮**触发 + 结果表。

**Rationale**: 用户明确列出检查项；固定序避免与可编排工艺混淆；互斥防止设备命令交错。

**Alternatives considered**:

- **自检步骤可配置顺序**：超出 v1 范围。
- **ICMP ping**：Windows 权限/防火墙不稳定；首版倾向 **TCP connect** 到已知设备端口。

## R8 — 全硬件 Mock 与可跑通交付

**Decision**: **进程内** `MockInstrumentHal` 覆盖 **全部** HAL 接口；用 **`--mock` / `INSTRUMENT_USE_MOCK=1`** 显式激活；主窗 **「仿真模式」** 角标；阶段耗时用 **`timeScale`** 压缩以便开发验收。

**Rationale**: 满足 FR-018 / SC-007；无硬件 CI 与培训演示；与真机共用 domain/UI。

**Alternatives considered**:

- **独立仿真进程 + IPC**：首版过重。
- **默认无标志即 Mock**：误判真机风险高，已拒绝（须显式）。

## R9 — GUI 美观与现代感（增量，/speckit-plan 2026-05-05）

**Decision**: 在 **Python + PySide6** 不变前提下，以 **（1）QSS / qt-material 级主题** 或 **（2）Fluent 风格 Widgets 组件库** 提升观感；**不**将主 GUI 迁出至 Electron/Tauri（除非未来宪章修订）。

**Rationale**: 符合 Principle IX；工业场景仍常见 Qt；Fluent/QSS 能以较低成本改善信息密度、圆角、导航与主色，满足「更加美观」而不分裂技术栈。

**Alternatives considered**:

- **全套迁移 QML**：动效最佳，但重写成本高、与现有 Widgets 对话框迁移路径长。  
- **Web 技术栈前端**：视觉灵活但与单机工控、离线部署及宪章 Python 主栈冲突，需显式例外。  
- **保持原生 Widgets 默认主题**：最简单，但无法满足本次「更美观」目标。
