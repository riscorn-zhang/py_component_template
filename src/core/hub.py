from __future__ import annotations

from typing import Callable, Dict, Set, Optional
import pluggy
import logging

from src.core.info import ComponentInfo
from src.core.interface import ComponentInterface

logger = logging.getLogger(__name__)


class ComponentHub:
    def __init__(self):
        self.managers: Dict[str, pluggy.PluginManager] = {}
        self.spec_hooks: Dict[str, pluggy.HookspecMarker] = {}
        self.impl_hooks: Dict[str, pluggy.HookimplMarker] = {}
        self.component_infos: Dict[str, ComponentInfo] = {}
        self.managers_components: Dict[str, Set[str]] = {}

    def _get_manager(self, name: str) -> pluggy.PluginManager:
        if name not in self.managers:
            self.managers[name] = pluggy.PluginManager(name)
        return self.managers[name]

    def create_manager(self, name: str, specs: list[Callable[..., type]] = []):
        manager = self._get_manager(name)
        for spec in specs:
            manager.add_hookspecs(spec(self))

    def get_manager(self, name: str) -> pluggy.PluginManager:
        return self._get_manager(name)

    def destroy_manager(self, name: str):
        if name in self.managers:
            manager = self.managers.pop(name)
            for plugin in list(manager.get_plugins()):
                manager.unregister(plugin)
            self.managers_components.pop(name, None)

    def get_components(self, manager_name: str) -> Set[ComponentInterface]:
        manager = self._get_manager(manager_name)
        return manager.get_plugins()

    def get_components_id(self, manager_name: str) -> Set[str]:
        return self.managers_components.get(manager_name, set())

    def get_component_info(self, component_id: str) -> Optional[ComponentInfo]:
        return self.component_infos.get(component_id)

    def register_component_info(self, component_info: ComponentInfo):
        meta = component_info.meta
        instance = component_info.instance
        self.component_infos[meta.id] = component_info

        for manager_name in meta.belong_managers:
            self.managers_components.setdefault(manager_name, set()).add(meta.id)
            self._get_manager(manager_name).register(instance, meta.id)

        try:
            instance.on_init()
        except Exception:
            logger.error(f"组件 {meta.id} 的 on_init 方法执行错误", exc_info=True)

    def del_component(self, component_id: str):
        info = self.component_infos.get(component_id)
        if not info:
            return

        try:
            info.instance.on_del()
        except Exception:
            logger.error(
                f"Error occurred while executing on_del method for component {component_id}",
                exc_info=True,
            )

        del self.component_infos[component_id]
        for manager_name in info.meta.belong_managers:
            manager = self._get_manager(manager_name)
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

    def bind_spec_to_manager(self, name: str, spec: Callable[..., type]):
        manager = self._get_manager(name)
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
            manager = self._get_manager(manager_name)
            hook = getattr(manager.hook, hook_name)
            return hook(*args, **kwargs)
        except AttributeError:
            raise AttributeError(
                f"Hook {hook_name} not found in manager {manager_name}"
            )
