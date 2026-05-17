import importlib
from typing import Dict, Callable, Type, List, Optional, Set

import pluggy

from src.core.descriptor import ComponentDescriptor
from src.core.interface import ComponentInterface


class ComponentSystem:
    def __init__(self):
        self.managers = {}
        self.spec_hooks: Dict[str, pluggy.HookspecMarker] = {}
        self.impl_hooks: Dict[str, pluggy.HookimplMarker] = {}
        self.spec_components = {}
        self.impl_components = {}

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

    def get_components(self, manager_name: str) -> Set[ComponentInterface]:
        manager = self.get_manager(manager_name)
        return manager.get_plugins()

    def get_components_id(self, manager_name: str) -> Set[str]:
        components: Set[ComponentInterface] = self.get_components(manager_name)
        return set(component.id for component in components)

    def del_component(self, component_id: str):
        component = self.impl_components.pop(component_id, None)
        if component:
            try:
                component.on_del()
            except Exception:
                pass
            for manager_name in component.belong_managers:
                manager = self.get_manager(manager_name)
                manager.unregister(component)

    def clear_components(self):
        for component_id in list(self.impl_components.keys()):
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

    def load_component(
        self, component_descriptor: ComponentDescriptor
    ) -> Optional[Type[ComponentInterface]]:
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

    def load_component_from_module(
        self, name: str
    ) -> Optional[Type[ComponentInterface]]:
        module = importlib.import_module(name)

        if not hasattr(module, "component"):
            raise RuntimeError(f"模块 {name} 没有 component 函数")

        try:
            return module.component(self)
        except TypeError as e:
            raise RuntimeError(f"模块 {name} 的 component 函数结构不匹配: {e}")
        except Exception as e:
            raise RuntimeError(f"加载模块 {name} 的 component 函数执行错误: {e}")

    def load_component_from_builtin(
        self, name: str
    ) -> Optional[Type[ComponentInterface]]:
        return self.load_component_from_module(f"src.components.{name}")

    def load_component_from_wheel(self, path: str):
        pass

    def load_component_from_package(self, package: str):
        pass

    def register_component_class(self, component_class: Type):
        """
        注册组件类
        """
        component = component_class()
        self.impl_components[component.id] = component
        for manager_name in component.belong_managers:
            self.get_manager(manager_name).register(component, component.id)
        try:
            component.on_init()
        except Exception:
            pass

    def register_component(self, component_descriptor: ComponentDescriptor):
        """
        注册组件的完整链
        Load + Register
        """
        component_class = self.load_component(component_descriptor)
        if component_class:
            self.register_component_class(component_class)
