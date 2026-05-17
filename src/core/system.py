from typing import Dict, Callable, Type, List, Set, Optional, Any

import pluggy
import importlib
import logging
import tomllib
from pathlib import Path

from src.core.info import (
    ComponentSourceDescriptor,
    ComponentMeta,
    ComponentInfo,
    ComponentDependencies,
)
from src.core.interface import ComponentInterface

logger = logging.getLogger(__name__)


class ComponentSystem:
    def __init__(self):
        self.managers = {}
        self.spec_hooks: Dict[str, pluggy.HookspecMarker] = {}
        self.impl_hooks: Dict[str, pluggy.HookimplMarker] = {}
        self.component_infos: Dict[str, ComponentInfo] = {}
        self.managers_components: Dict[str, Set[str]] = {}

    def create_manager(self, name: str, specs: List[Callable[..., Type]] = []):
        manager: pluggy.PluginManager = self.get_manager(name)
        for spec in specs:
            manager.add_hookspecs(spec(self))

    def get_manager(self, name: str) -> pluggy.PluginManager:
        if name not in self.managers:
            self.managers[name] = pluggy.PluginManager(name)
        return self.managers[name]

    def destroy_manager(self, name: str):
        if name in self.managers:
            manager = self.managers.pop(name)
            for plugin in list(manager.get_plugins()):
                manager.unregister(plugin)
            self.managers_components.pop(name, None)

    def get_components(self, manager_name: str) -> Set[ComponentInterface]:
        manager = self.get_manager(manager_name)
        return manager.get_plugins()

    def get_components_id(self, manager_name: str) -> Set[str]:
        return self.managers_components.get(manager_name, set())

    def del_component(self, component_id: str):
        info = self.component_infos.get(component_id, None)
        if info:
            try:
                info.instance.on_del()
            except Exception:
                logger.error(
                    f"组件 {component_id} 的 on_del 方法执行错误", exc_info=True
                )

            del self.component_infos[component_id]

            for manager_name in info.meta.belong_managers:
                manager = self.get_manager(manager_name)
                manager.unregister(info.instance)
                self.managers_components[manager_name].remove(component_id)
                if not self.managers_components[manager_name]:
                    self.managers_components.pop(manager_name, None)

    def clear_components(self):
        for component_id in list(self.component_infos.keys()):
            self.del_component(component_id)

    def shutdown(self):
        self.clear_components()
        self.managers.clear()

    def bind_spec_to_manager(self, name: str, spec: Callable[..., Type]):
        manager: pluggy.PluginManager = self.get_manager(name)
        manager.add_hookspecs(spec(self))

    def get_spec_hook(self, name: str) -> pluggy.HookspecMarker:
        if name not in self.spec_hooks:
            self.spec_hooks[name] = pluggy.HookspecMarker(name)
        return self.spec_hooks[name]

    def get_impl_hook(self, name: str) -> pluggy.HookimplMarker:
        if name not in self.impl_hooks:
            self.impl_hooks[name] = pluggy.HookimplMarker(name)
        return self.impl_hooks[name]

    def execute_hook(self, manager_name: str, hook_name: str, *args, **kwargs):
        try:
            manager = self.get_manager(manager_name)
            hook = getattr(manager.hook, hook_name)
            return hook(*args, **kwargs)
        except AttributeError:
            raise AttributeError(
                f"Hook {hook_name} not found in manager {manager_name}"
            )

    def parse_toml_meta(self, file: str) -> ComponentMeta:
        """
        解析组件目录下的 meta.toml,返回结构化的 ComponentMeta 对象。
        :param path: meta.toml 文件路径
        """

        path = Path(file)
        if not path.is_file():
            raise FileNotFoundError(f"meta.toml not found: {path}")
        with path.open("rb") as f:
            raw: Dict[str, Any] = tomllib.load(f)

        required_fields = ["id", "name", "version", "belong_managers"]
        for field_name in required_fields:
            if field_name not in raw:
                raise ValueError(f"Missing required field '{field_name}' in {path}")

        deps_raw = raw.get("dependencies", {})

        dependencies = ComponentDependencies(
            python=list(deps_raw.get("python", []) or []),
            components=list(deps_raw.get("components", []) or []),
        )

        meta = ComponentMeta(
            id=raw["id"],
            name=raw["name"],
            version=raw["version"],
            description=raw.get("description"),
            belong_managers=list(raw.get("belong_managers", []) or []),
            dependencies=dependencies,
        )
        return meta

    def load_component(
        self, component_descriptor: ComponentSourceDescriptor
    ) -> Optional[ComponentInfo]:
        """
        load_component 系列函数：
        通过函数动态生成Class,加载组件类型,但并未实现组件注册
        """
        if component_descriptor.type == "module":
            return self.load_component_from_module(component_descriptor.location)
        elif component_descriptor.type == "builtin":
            return self.load_component_from_builtin(component_descriptor.location)
        elif component_descriptor.type == "wheel":
            return self.load_component_from_wheel(component_descriptor.location)
        elif component_descriptor.type == "package":
            return self.load_component_from_package(component_descriptor.location)
        else:
            raise RuntimeError(f"未知的组件类型: {component_descriptor.type}")

    def load_component_from_module(self, name: str) -> Optional[ComponentInfo]:
        module = importlib.import_module(name)

        for method_name in ["component", "meta_path"]:
            if not (hasattr(module, method_name)):
                raise RuntimeError(f"模块 {name} 没有 {method_name} 函数")

        try:
            info = ComponentInfo(
                meta=self.parse_toml_meta(module.meta_path()),
                instance=module.component(self)(),
            )
            return info
        except TypeError as e:
            raise RuntimeError(
                f"模块 {name} 的 component 或 meta_path 函数结构不匹配: {e}"
            )
        except Exception as e:
            raise RuntimeError(f"加载模块 {name} 的 component 函数执行错误: {e}")

    def load_component_from_builtin(self, name: str) -> Optional[ComponentInfo]:
        return self.load_component_from_module(f"src.components.{name}")

    def load_component_from_wheel(self, path: str):
        pass

    def load_component_from_package(self, package: str):
        pass

    def register_component_to_system(self, component_info: ComponentInfo):
        """
        注册组件类（接受 ComponentInfo，以便保留 module_name 等元数据）
        """
        meta = component_info.meta
        instance = component_info.instance
        self.component_infos[meta.id] = component_info

        # 维护 managers -> set(component_id) 的映射，便于按 manager 清理
        for manager_name in meta.belong_managers:
            self.managers_components.setdefault(manager_name, set()).add(meta.id)
            self.get_manager(manager_name).register(instance, meta.id)

        try:
            instance.on_init()
        except Exception:
            logger.error(f"组件 {meta.id} 的 on_init 方法执行错误", exc_info=True)

    def register_component(self, component_descriptor: ComponentSourceDescriptor):
        """
        注册组件的完整链
        Load + Register
        """
        component_info = self.load_component(component_descriptor)
        if component_info:
            self.register_component_to_system(component_info)
