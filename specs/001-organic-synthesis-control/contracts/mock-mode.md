# Contract: Mock（仿真）模式

**Normative**：补充 [spec.md](../spec.md) FR-018、[plan.md](../plan.md) § 全硬件 Mock。

## 激活（须至少实现其一，且优先级与 plan 一致）

| 机制 | 示例 |
|------|------|
| CLI | `InstrumentApp.exe --mock` |
| 环境变量 | `INSTRUMENT_USE_MOCK=1` |
| 配置文件 | `instrument.json` → `"runMode": "mock"` |

## 行为要求

1. **HAL**：所有通过 `IInstrumentHal`（及子接口）下发的设备动作 **不得** 触碰真实总线/串口；Mock 返回可配置延迟与成功/失败。
2. **环境读数**：Mock 模式下 `AmbientReading` 来自 **模拟源**（缓慢漂移的正弦或阶跃），`valid=true`，除非测试注入无效。
3. **自检**：第 3–6 步（泵、阀、回零、冷热水机）**必须**走 Mock；第 1–2 步默认 **真实 OS**（磁盘/网卡）；若 CI 需全软通过，在 `mock.json` 设 `softNetworkDisk: true`，两步立即 Pass 并写日志说明。
4. **UX**：主窗 **须**含「仿真模式」可视指示；不得与 Production 视觉混淆。

5. **禁止**：静默以 Mock 冒充真机（无开关默认 Mock）。

## 非目标（v1）

- 行为级**比特级**对齐某厂家协议。
- 分布式跨机仿真。
