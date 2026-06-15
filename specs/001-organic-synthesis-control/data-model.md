# Data Model: 有机合成仪器控制软件

**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## 应用运行模式

| 枚举 | 说明 |
|------|------|
| `Production` | `RealInstrumentHal`（真机） |
| `Mock` | `MockInstrumentHal`（FR-018）；**须在 UI 显著标示** |

解析优先级（计划）：命令行 `--mock` > 环境变量 `INSTRUMENT_USE_MOCK=1` > `instrument.json`。

## 枚举：`BusinessPhase`

`加粉` | `反应` | `萃取` | `蒸馏` | `过滤` | `取样`

（存储可用英文常量 `POWDER / REACTION / EXTRACTION / DISTILLATION / FILTRATION / SAMPLING`，界面显示中文。）

## 1. Recipe（实验方法）

| 字段 | 说明 | 验证 |
|------|------|------|
| `id` | UUID 或本地唯一 | 必填 |
| `name` | 显示名 | 必填 |
| `revisionAt` | ISO8601 | 必填 |
| `parameters` | FR-001 参数集 | FR-002 |
| `steps[]` | **有序** `RecipeStep` 列表 | 长度 ≥ 1；每项 `businessPhase` 合法 |

### RecipeStep

| 字段 | 说明 |
|------|------|
| `stepUid` | 稳定 ID（UUID），便于日志与恢复 |
| `orderIndex` | 0..n-1，与数组顺序一致（持久化时可重算） |
| `businessPhase` | ∈ BusinessPhase |
| `planDurationSec` | ETA 用；`反应` 未填时可回退到 `parameters.反应时间`（产品规则在 domain 实现） |
| `deviceArgs` | JSON/结构化参数，按 `businessPhase` 解释 |
| `displayOverride` | 可选；覆盖状态栏显示（极少用） |

**重复**: 多行可有相同 `businessPhase`；由 `stepUid` 区分。

## 2. Run

| 字段 | 说明 |
|------|------|
| `id` | 运行 ID |
| `recipeId` | 引用 Recipe |
| `startedAt` / `endedAt` | 时间戳 |
| `phase` | Idle / Running / Paused / Failed / Completed |
| `currentStepIndex` | 指向 `steps[currentStepIndex]` |
| `stepStatuses[]` | 与 `steps[]` 等长 |
| `alarms[]` | FR-009 |

推进规则：**仅** `currentStepIndex++`（成功完成后）或失败停驻；不调序、不跳过除非另版 spec。

## 3. AmbientReading / UserDisplayPrefs

（同前；略）

## 4. StatusBarViewModel

`currentAction` **默认** = `steps[currentStepIndex].businessPhase` 的中文标签；若 `displayOverride` 则用之。

## 5. Run 状态转换

（同前）

## 6. 自检（Self-test）

### 枚举 `SelfTestStepId`

`Network` | `DiskSpace` | `PumpInit` | `RotaryValveInit` | `StepperHome` | `ChillerComm`

顺序 **固定** 与 FR-015 一致；**禁止**用户重排（v1）。

### SelfTestRun

| 字段 | 说明 |
|------|------|
| `id` | UUID |
| `startedAt` / `endedAt` | 时间戳 |
| `overallPass` | bool |
| `items[]` | `SelfTestItemResult` 列表，顺序同上 |

### SelfTestItemResult

| 字段 | 说明 |
|------|------|
| `stepId` | SelfTestStepId |
| `status` | `passed` \| `failed` \| `not_run` |
| `message` | 人类可读 |
| `durationMs` | 可选 |

`not_run` 仅因**前置步骤失败跳过**而出现，不得与 `passed` 混淆。

