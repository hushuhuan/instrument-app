# Quickstart: 有机合成仪器控制软件（开发向）

**Plan**: [plan.md](./plan.md) | **Mock 契约**：[contracts/mock-mode.md](./contracts/mock-mode.md)

## 前提

- Windows 10/11 x64
- CMake 3.22+、兼容 C++20 的工具链（MSVC 2022 或 LLVM）
- Qt 6.5+ 安装并设好 `CMAKE_PREFIX_PATH`（指向 Qt 的 lib/cmake）

## 获取代码后（结构落实后）

```powershell
cmake -S . -B build -DCMAKE_PREFIX_PATH="C:/Qt/6.x.x/msvc2019_64"
cmake --build build --config Release
```

## 仿真（Mock）— 推荐日常开发路径（FR-018）

### Python 桌面应用（`instrument-app`，Principle IX）

1. `pip install -e ".[dev]"`
2. `instrument-app --mock`
3. 可选环境变量：
   - `INSTRUMENT_USE_MOCK=1`：等价于 `--mock`（CLI 优先）。
   - `INSTRUMENT_TEST_HOOKS=1`：启用 Mock **故障注入**（仅测试/排障；如强制 `init_pumps` 失败）。
   - `INSTRUMENT_HAL_DEBUG=0`：关闭对泵/阀/冷机的 **调试指令**（设备调试页将拒绝写操作）。
4. 日志目录（相对当前工作目录）：`logs/selftest.log`、`logs/debug_device.log`、`logs/alarms.log`。
5. 开发：菜单 **调试 → 导出状态栏快照…** 可写出符合 `contracts/status-bar-state.schema.json` 的 JSON（排障/契约核对）。

### CMake / C++ 构建路径（旧版结构，若仓库中仍存在）

**目标**：**零硬件**跑完整程序 — GUI、方法编辑、流程运行、自检（设备项为模拟）、状态栏。

1. **启动**（任选其一）：
   - `.\InstrumentApp.exe --mock`
   - 或：`$env:INSTRUMENT_USE_MOCK="1"; .\InstrumentApp.exe`
2. **确认**：窗口显示 **「仿真模式」**；标题栏或顶栏与真机版本可区分。
3. **验证流程**：
   - 编辑/保存一份含 **非模板顺序** + **重复阶段** 的方法；
   - **开始运行** → 观察阶段推进与状态栏 **剩余时间**（Mock 下可能因 `timeScale` 缩短）；
   - **暂停 / 恢复** 至少各一次。
4. **验证自检**：在 **Run 空闲**时点击 **「自检」**；设备相关步应快速完成；可在测试菜单对 Mock 注入 **DiskSpace** 失败，确认后续 **`not_run`**。
5. **环境读数**：状态栏温湿度应连续变化（模拟源）；切换 **℃ / ℉** 生效。

### CI / 无网卡环境（可选）

若 `mock.json`（或等价配置）中 `softNetworkDisk: true`，自检前两步可短路为 Pass（须打日志）。默认开发机建议 **关闭**，以暴露本机磁盘/网络问题。

## 真机模式（日后）

不传入 `--mock` 且环境变量未置位 → `Production` → `RealInstrumentHal`（实现完成后）。

## 验证契约

- 状态栏快照：`contracts/status-bar-state.schema.json`
- 自检汇总：`contracts/self-test-report.schema.json`
- 模式语义：`contracts/mock-mode.md`

## 相关文档

- 步骤→状态栏映射：[contracts/workflow-step-mapping.md](./contracts/workflow-step-mapping.md)
- 数据：[data-model.md](./data-model.md)
