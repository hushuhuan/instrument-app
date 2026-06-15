# 有机合成仪器控制（Instrument control）

实验室单机桌面程序：工艺参数与方法编排、运行与状态栏、仪器 HAL、Mock 仿真与自检。实现栈为 **Python 3.11+** 与 **PySide6（Qt 6）**，见项目宪章 [`.specify/memory/constitution.md`](.specify/memory/constitution.md) Principle IX。

## 文档

- 功能说明与契约：[specs/001-organic-synthesis-control/](specs/001-organic-synthesis-control/)
- 快速上手：[specs/001-organic-synthesis-control/quickstart.md](specs/001-organic-synthesis-control/quickstart.md)
- 实现计划：[specs/001-organic-synthesis-control/plan.md](specs/001-organic-synthesis-control/plan.md)

## 环境与运行

源码包 layout：`pyproject.toml` 指向 `src/instrument_app/`。

```bash
cd /path/to/CPP
py -m pip install -e ".[dev]"
instrument-app --mock
```

等价入口：

```bash
py -m instrument_app.app.main --mock
```

**Mock / 仿真**：命令行 `--mock`，或环境变量 `INSTRUMENT_USE_MOCK=1`（与 `instrument.json` 等的优先级以 [mock-mode 契约](specs/001-organic-synthesis-control/contracts/mock-mode.md) 为准）。

## 测试

```bash
py -m pytest tests/ -q
```

## 源码布局（简要）

```text
src/instrument_app/
├── app/           # 入口与 ApplicationContext
├── domain/        # 配方、运行协调、校验、自检编排
├── hal/           # 仪器抽象、Mock / Real 实现
├── persistence/   # 本地 JSON 等方法持久化
└── ui/            # 主窗、对话框、状态栏、样式
```
