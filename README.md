# 组件化 Python 项目模板（py-component-template）

一个基于 **pluggy + pydantic** 的组件化 / 插件化 Python 项目模板，用来快速搭建「组件化 Python 应用」。  
通过统一的组件接口、描述符和插件管理系统，让应用的功能可以按组件进行拆分、加载和注册。

## 特性概览

- 基于 **pluggy** 的插件机制：
  - 通过「spec / impl」模式定义和实现 Hook。
  - 示例中提供了 `app` 这一套规范及其实现。
- 明确的组件接口：
  - 所有组件实现统一的 `ComponentInterface`。
  - 支持组件 ID、名称、归属管理器、依赖等信息。
- 组件描述符（Descriptor）：
  - 使用 `ComponentDescriptor` 描述组件来源（模块 / 文件 / 包等）。
  - 当前示例实现了从 **模块** 加载组件的流程。
- 组件系统（ComponentSystem）：
  - 统一管理 pluggy 的 `PluginManager`。
  - 提供创建管理器、绑定 spec、注册组件、执行 hook 的能力。
- 公共命名空间：
  - `configs.py`：用户配置的全局命名空间。
  - `globals.py`：程序运行期生成/维护的全局命名空间。
  - `public_namespace.py`：对外统一暴露 `configs` 和 `globals`。

这是一个**模板工程**，你可以基于它去开发具体业务项目，而不是直接作为业务项目本身。

---

## 项目结构

```text
py-component-template/
├─ pyproject.toml           # 项目元数据与依赖（pluggy, pydantic）
├─ README.md                # 项目说明（本文件）
├─ uv.lock                  # uv 依赖锁定文件
└─ src/
   ├─ main.py               # 程序入口，演示如何创建系统并启动 app
   ├─ configs.py            # 用户可自定义的全局配置命名空间
   ├─ globals.py            # 程序运行时的全局命名空间
   ├─ public_namespace.py   # 统一导出 configs 和 globals
   ├─ sugar.py              # 语法糖/占位函数
   └─ core/
      ├─ interface.py       # 组件接口定义：ComponentInterface
      ├─ descriptor.py      # 组件描述符：ComponentDescriptor
      ├─ system.py          # 组件系统：ComponentSystem
      ├─ specs/
      │  └─ app.py          # app 相关的 hookspec 定义（start_app）
      └─ components/
         ├─ entry/
         │  └─ component.py # 示例入口组件，对 app.start_app 进行实现
         ├─ service/
         │  └─ component.py # 预留 service 组件模板
         └─ client/
            └─ component.py # 预留 client 组件模板
```

---

## 快速开始

### 环境要求

- Python `>= 3.11`
- 已安装 uv [<sup>1</sup>](https://github.com/astral-sh/uv) 或使用 `pip`/`venv` 也可以。

### 安装依赖

如果你使用 uv（推荐）：

```bash
uv sync
```

或使用 pip：

```bash
pip install -r <根据需要生成的依赖文件> 
# 或手动安装
pip install pluggy>=1.6.0 pydantic>=2.13.4
```

### 运行示例程序

在项目根目录执行：

```bash
python -m src.main arg1 arg2
```

或：

```bash
python src/main.py arg1 arg2
```

你将看到类似输出：

```text
Starting app...
Arguments: ['src/main.py', 'arg1', 'arg2']
```

这表示：

1. `ComponentSystem` 创建了名为 `app` 的插件管理器；
2. 加载并注册了 `entry` 组件；
3. 调用了 `app` 管理器上的 `start_app` hook；
4. `entry` 组件通过 hookimpl 实现了 `start_app`，打印出启动信息和命令行参数。

---

## 组件系统设计说明

### 1. 组件接口：`ComponentInterface`

位于 `src/core/interface.py`。所有组件都应实现该接口：

- 必须实现的属性 / 方法：
  - `id: str` —— 组件唯一标识符
  - `name: str` —— 组件显示名称
  - `belong_managers: List[str]` —— 组件归属的管理器名（可以多个）
  - `on_init()` —— 组件初始化时调用
  - `on_del()` —— 组件卸载/销毁时调用
- 可选实现：
  - `dependencies: List[str]` —— 依赖的其他组件 ID（默认空列表）

### 2. 组件描述符：`ComponentDescriptor`

位于 `src/core/descriptor.py`，基于 pydantic 的 `BaseModel`：

```python
class ComponentDescriptor(BaseModel):
    type: Literal["module", "builtin", "file", "package"]
    location: str
```

示例中使用：

```python
ComponentDescriptor(
    type="module",
    location="src.core.components.entry.component"
)
```

表示：从 `src.core.components.entry.component` 模块中加载组件。

### 3. 组件系统：`ComponentSystem`

位于 `src/core/system.py`，职责包括：

- 管理多个插件管理器（`PluginManager`）：
  - `create_manager(name, specs)`：创建管理器并绑定 spec。
  - `get_manager(name)`：获取（或懒创建）指定名字的管理器。
  - `del_manager(name)`：删除管理器。
- Spec / Impl Hook 标记器：
  - `get_spec_hook(name)`：获取 HookspecMarker。
  - `get_impl_hook(name)`：获取 HookimplMarker。
- 组件加载与注册：
  - `load_component(descriptor)`：根据 `ComponentDescriptor` 加载组件类（目前支持 `type="module"`）。
  - `register_component_class(cls)`：实例化组件，按其 `belong_managers()` 注册到对应 manager。
  - `register_component(descriptor)`：完整的加载 + 注册链路。
- 执行 hook：
  - `execute_hook(manager_name, hook_name, *args, **kwargs)`  
    eg. `execute_hook("app", "start_app", argv=...)`

---

## 示例：定义一个 App Hook 规范

位于 `src/core/specs/app.py`，定义了 app 层面的 hook 规范：

```python
def spec(system: ComponentSystem):
    hookspec = system.get_spec_hook("app")

    class AppSpec:
        @hookspec
        def start_app(self, argv: List[str]):
            pass

    return AppSpec
```

该规范通过 `create_manager("app", [app_spec])` 绑定到 `app` 管理器上。

---

## 示例：实现一个入口组件

位于 `src/core/components/entry/component.py`：

```python
def component(system: ComponentSystem) -> Type[ComponentInterface]:
    hookimpl = system.get_impl_hook("app")

    class EntryComponent(ComponentInterface):
        def dependencies(self) -> List[str]:
            return []

        def id(self) -> str:
            return "entry"

        def name(self) -> str:
            return "Entry"

        def belong_managers(self) -> List[str]:
            return ["app"]

        def on_del(self):
            pass

        def on_init(self):
            pass

        @hookimpl
        def start_app(self, argv: List[str]):
            print("Starting app...")
            print("Arguments:", argv)

    return EntryComponent
```

注意这里的约定：

- 模块必须暴露一个 `component(system)` 函数；
- 该函数返回一个实现了 `ComponentInterface` 的类；
- 在类中使用 `hookimpl` 装饰器实现对应 hook。

`ComponentSystem` 会：

1. 通过 `importlib` 加载模块；
2. 调用模块的 `component(system)` 函数得到组件类；
3. 实例化组件并注册到它声明的 `belong_managers()` 对应的 manager。

---

## 如何基于模板扩展

当你把这个项目作为模板使用时，可以按以下步骤扩展：

1. **新增一个 Hook 规范（spec）**
   - 在 `src/core/specs/` 下新增文件，例如 `user.py`；
   - 定义一个 `spec(system: ComponentSystem)` 函数，里面定义新的 hook 接口。

2. **为某个功能编写组件**
   - 在 `src/core/components/` 下新建目录，例如 `user/`；
   - 在其中创建 `component.py`；
   - 实现 `component(system)` 函数，返回实现 `ComponentInterface` 的类；
   - 在类中使用 `system.get_impl_hook("<manager_name>")` 定义 hookimpl。

3. **在入口代码中注册新组件**
   - 修改 `src/main.py`：
     - 给 `ComponentSystem` 创建或绑定新的 manager/spec；
     - 使用 `ComponentDescriptor` 描述你的新组件模块；
     - 调用 `system.register_component(...)` 完成注册；

4. **使用 configs / globals 作为公共命名空间**
   - 在 `configs.py` 中写入用户可配置项；
   - 在 `globals.py` 中写入运行期需要维护的全局状态；
   - 在组件或入口中通过 `from src.public_namespace import configs, globals` 统一使用。

---

## 后续计划 / TODO

- [ ] 完善 `load_component_from_file` / `load_component_from_package` 实现；
- [ ] 在 `service` / `client` 目录中给出更完整的示例组件；
- [ ] 增加简单的日志、错误处理示例；
- [ ] 增加测试用例和 CI 配置；
- [ ] 编写更多文档（如：最佳实践、FAQ、典型架构示例）。

---

如果你有特定的使用场景（例如：Web 项目、CLI 工具、游戏脚本等），可以告诉我，我能再帮你把 README 调整成更贴近该场景的描述与示例。