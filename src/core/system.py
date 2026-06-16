import logging
from types import ModuleType
from typing import Any, List, Dict
from collections import defaultdict, deque

from src.core.hub import ComponentHub
from src.core.info import ComponentSourceDescriptor, ComponentMeta
from src.core.loader import ComponentLoader
from src.core.lib_provider import ComponentLibProvider
from src.vars.debug import EXC_INFO
from src.sugar import temperory_placeholder

logger = logging.getLogger(__name__)


class ComponentSystem:
    def __init__(self) -> None:
        self.hub = ComponentHub()
        self.loader = ComponentLoader()
        self.lib_provider = ComponentLibProvider()

    def _check_component_dependencies(self, meta: ComponentMeta) -> bool:
        missing = [
            dependency
            for dependency in meta.dependencies.components
            if dependency not in self.hub.component_infos
        ]
        if missing:
            logger.error(
                "Component '%s' cannot be loaded because missing component dependencies: %s",
                meta.id,
                missing,
            )
            return False
        return True

    def __components_dependencies_filter(
        self, metas: Dict[str, ComponentMeta]
    ) -> List[str]:
        installed_ids = set(self.hub.get_components_ids())
        new_ids = set(metas.keys())

        avaliable = installed_ids | new_ids

        # 1.预处理.先剔除依赖不存在的组件
        for node in new_ids:
            for dep in metas[node].dependencies.components:
                if dep not in avaliable:
                    logger.error(
                        "Component '%s' cannot be loaded because missing component dependency: %s",
                        node,
                        dep,
                    )
                    new_ids.remove(node)
                    break

        # 2.构建依赖图

        dep_graph = defaultdict(set)
        in_degree = {node: 0 for node in new_ids}

        for node in new_ids:
            for dep in metas[node].dependencies.components:
                if dep in new_ids:
                    dep_graph[dep].add(node)
                    in_degree[node] += 1

        # 3.拓扑排序
        queue = deque([node for node in new_ids if in_degree[node] == 0])
        sorted_ids = []

        while queue:
            curr = queue.popleft()
            sorted_ids.append(curr)
            for dep in dep_graph[curr]:
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)

        return sorted_ids

    def shutdown(self) -> None:
        self.hub.shutdown()

    def execute_hook(
        self, manager_name: str, hook_name: str, *args: Any, **kwargs: Any
    ) -> Any:
        return self.hub.execute_hook(manager_name, hook_name, *args, **kwargs)

    exec_ = x = hook = execute_hook

    def register_component(
        self, component_descriptor: ComponentSourceDescriptor
    ) -> None:
        try:
            module = self.loader.load_component_module(component_descriptor)
            component_info = self.loader.load_component(module, self)
            if component_info:
                self.hub.register_component_info(component_info)
        except Exception:
            logger.error(
                "Unexpected failure registering component descriptor %s",
                exc_info=EXC_INFO,
            )

    def batch_register_components(
        self, component_descriptors: list[ComponentSourceDescriptor]
    ) -> None:
        modules = [
            self.loader.load_component_module(component_descriptor)
            for component_descriptor in component_descriptors
        ]

        metas = {}
        module_dict = {}

        for module in modules:
            meta = self.loader.load_component_meta(module)
            if meta:
                metas[meta.id] = meta
                module_dict[meta.id] = module

        will_install_components_ids = self.__components_dependencies_filter(metas)

        for install_id in will_install_components_ids:
            module = module_dict[install_id]
            component_info = self.loader.load_component(module, self)
            if component_info:
                self.hub.register_component_info(component_info)

    def import_(self, module_name: str) -> ModuleType:
        raise NotImplementedError()

    def import_all_from(self, module_name: str) -> ModuleType:
        raise NotImplementedError()

    def from_import(self, module_name: str) -> ModuleType:
        raise NotImplementedError()
