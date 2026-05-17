下面是一个适合你这个仓库的新版 `README.md` 草稿，你可以直接覆盖现有的 README 使用，再根据实际情况微调。

---

# py_component_template

一个用于快速搭建「组件化 Python 应用」的项目模板。  
提供统一的组件目录结构、元信息描述（`meta.toml`）、加载与运行规范，适合用来写插件式 / 业务组件式的项目。

---

## 目录结构

项目的核心代码位于 `src/` 目录：

```text
src/
  main.py               # 程序入口
  sugar.py              # 一些语法糖/辅助函数
  specs/
    app.py              # 应用规格定义（如应用级生命周期、启动流程等）
  core/
    info.py             # 组件/应用信息相关的数据结构
    interface.py        # 组件接口约定（抽象类/协议）
    system.py           # 组件系统/加载运行的核心逻辑
  vars/
    configs.py          # 配置相关变量
    infos.py            # 信息类变量（组件信息、应用信息）
    runtimes.py         # 运行时状态
    vars.py             # 统一汇总/导出变量
  components/           # 业务组件（按类型划分）
    client/
      meta.toml         # 该组件的元信息（名称、描述、依赖等）
      __init__.py       # 具体组件实现，对外暴露 component() / meta_path()
    entry/
      meta.toml
      __init__.py
    service/
      meta.toml
      __init__.py
    pypack_support/     # 预留给打包/发布支持用的组件或工具（当前为空）
```

其他文件：

- `pyproject.toml`：项目依赖与构建配置（使用 PDM/uv/poetry 等工具时的统一入口）。
- `.venv/`：本地虚拟环境目录（建议在版本管理中忽略，只保留示例或 `.venv/.gitignore`）。
- `uv.lock`：使用 `uv` 管理依赖时生成的锁定文件。

---

## 组件规范

每一个组件目录（如 `src/components/client`）通常包含：

- `meta.toml`：组件的元信息，示例字段可以包括：

  ```toml
  name = "client"
  description = "示例客户端组件"
  version = "0.1.0"
  # 其他你需要的字段
  ```

- `__init__.py`：组件实现文件，需要遵守统一约定，对外至少暴露两个函数：

  ```python
  def component(system) -> object:
      """
      返回该组件的实例。
      system 参数通常是 core.system 中的系统对象，
      用来访问全局配置、日志、其他组件等。
      """
      ...

  def meta_path() -> str:
      """
      返回 meta.toml 的路径，
      由 core.system / loader 读取并解析元信息。
      """
      ...
  ```

核心加载逻辑大致是（伪代码）：

```python
import importlib

module = importlib.import_module("components.client")

# 要求模块中必须有 component / meta_path 两个函数
instance = module.component(system)
meta_file = module.meta_path()
# 再由 core.info / core.system 等解析 meta_file 并注册组件
```

---

## 快速开始

### 1. 创建虚拟环境并安装依赖

如果你使用 `uv`（推荐）：

```bash
cd py_component_template
uv sync
```

或使用 Python 自带 venv + pip：

```bash
cd py_component_template
python -m venv .venv
.\.venv\Scripts\activate   # Windows PowerShell / CMD
pip install -r requirements.txt  # 如果你另外导出了依赖
```

如果依赖全部写在 `pyproject.toml` 中，也可以根据你的工具（如 `pdm`, `poetry`）来安装。

### 2. 运行示例应用

```bash
# 进入虚拟环境后
python -m src.main
# 或者
python src/main.py
```

具体入口以 `src/main.py` 中的实现为准。

---

## 新增一个组件

以新增一个 `report` 组件为例：

1. 创建目录结构：

   ```text
   src/components/report/
     meta.toml
     __init__.py
   ```

2. 编写 `meta.toml`：

   ```toml
   name = "report"
   description = "报表/统计组件"
   version = "0.1.0"
   ```

3. 在 `__init__.py` 中实现规范接口：

   ```python
   from pathlib import Path

   def meta_path() -> str:
       return str(Path(__file__).with_name("meta.toml"))

   class ReportComponent:
       def __init__(self, system):
           self.system = system

       def run(self):
           print("report component running")

   def component(system) -> ReportComponent:
       return ReportComponent(system)
   ```

4. 根据 `core/system.py` 中的加载逻辑，让系统去加载这个新组件（通常是通过配置或枚举组件列表实现）。

---

## 适用场景

- 想要一个**统一结构**组织多个业务组件/插件；
- 希望组件有**独立的元信息**（名称、描述、版本、配置等），便于管理和展示；
- 想利用 `importlib` 和统一接口实现一种**插件系统**或**模块化架构**。

---

## 开发建议

- 统一使用包路径（如 `components.client`），避免在动态导入时产生大量不同的模块名，导致 `sys.modules` 无意义增长。
- 对组件接口（如 `component()` / `meta_path()`）使用 `pydantic` 或类型标注进行约束，可以减少运行时出错。
- 在 `core/` 下集中管理：
  - 组件加载与注册逻辑；
  - 日志与错误处理；
  - 配置与运行时上下文。

---

如果你希望 README 更偏向「库」风格（比如发到 PyPI），或者希望加上安装指引、示例代码片段，我可以在这个基础上再给你一份面向“第三方使用者”的版本。