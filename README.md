# py_component_template

这是一个本地运行型的组件化 Python 项目模板。它不会依赖 pip 安装、npm 安装或包发布机制，适合以“项目内部可扩展组件”的方式组织代码。

## 设计原则

- 本地运行优先：通过 `python src/main.py` 启动。
- 组件化结构：每个组件独立目录，包含 `meta.toml` 与 `__init__.py`。
- 最小耦合：不依赖 `entry_points`、`build-system` 或包发布。
- 可扩展性：新增组件时只需补配置，不改变运行架构。

## 目录概览

```text
src/
  main.py                # 程序入口
  sugar.py               # 运行时辅助函数
  specs/                 # hook 规范定义
    app.py
  core/                  # 组件系统核心实现
    hub.py
    info.py
    interface.py
    loader.py
    packload.py
    system.py
  vars/                  # 运行时配置、状态与辅助函数
    configs.py
    infos.py
    runtimes.py
    functions.py
  components/            # 本地组件目录
    client/
      meta.toml
      __init__.py
    entry/
      meta.toml
      __init__.py
    service/
      meta.toml
      __init__.py
    lib_support/         # 预留支持工具目录
```

## 核心说明

### 1. 这是“本地项目模板”，不是“可发布库”

你当前项目的目标是：

- 在本地运行；
- 通过组件目录加载扩展；
- 维持运行时与组件结构的清晰。

因此无需：

- `pip install .`
- `build-system` 配置
- `entry_points`
- 发布到 PyPI

这样可以避免与 Python 打包生态的额外耦合，更符合你“保持项目整洁”的需求。

### 2. 运行方式

在项目根目录执行：

```bash
python src/main.py
```

或者：

```bash
python -m src.main
```

如果需要隔离环境，可以使用虚拟环境，但这只用于本地开发，不是发布要求：

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt  # 如果你额外导出了依赖
```

### 3. 依赖声明说明

`pyproject.toml` 仅用于声明运行时依赖，它并不是必须用于发布。也就是说，你可以把它当作“项目依赖清单”，而不是“包发布配置”。

## 组件规范

每个组件目录包含：

- `meta.toml`：组件元信息
- `__init__.py`：组件实现入口

当前加载器会读取组件目录的 `__init__.py`，并使用同级目录下的 `meta.toml` 注册组件。

### meta.toml 示例

```toml
id = "app.cmdcli"
name = "Command Line Interface"
version = "0.1.0"
description = "The command line interface of the application."
belong_managers = ["app"]

[dependencies]
python = []
components = []
```

### 组件实现约定

组件模块需要提供一个 `component(system)` 函数，返回组件类或组件实例。

示例：

```python
from src.core.system import ComponentSystem
from src.core.interface import ComponentInterface


def component(system: ComponentSystem):
    class MyComponent(ComponentInterface):
        def on_init(self):
            pass

        def on_del(self):
            pass

    return MyComponent
```

## 快速扩展

### 新增组件步骤

1. 创建目录： `src/components/<component_name>/`
2. 添加 `meta.toml`
3. 添加 `__init__.py`，实现 `component(system)`
4. 将目录路径加入 `src/vars/configs.py` 的 `INIT_COMPONENTS`

### 运行示例

当前项目默认加载：

- `src/components/service`
- `src/components/client`
- `src/components/entry`

`src/main.py` 会按 `src/vars/configs.py` 的配置注册组件，并最终调用 `app` manager 的 `entry` hook。

## 为什么这样设计

- 你不需要把扩展当成 Python 包来发布；
- 你不需要把组件绑定到 `pip` 或 `npm` 生态；
- 你只需在项目内部按约定管理组件即可；
- 这种设计更适合“项目级插件/模块化架构”。

## 进一步优化建议

- 继续保持 `src/components/` 目录作为本地组件源；
- 使用 `meta.toml` 记录组件依赖和归属管理器；
- 保持 `src/core/` 作为运行时加载与 hook 调度核心。

---

如果你愿意，我也可以继续帮你把这个模板进一步精简成“更纯粹的组件加载器 + 最少运行时依赖”版本。