<<<<<<< HEAD
from typing import Callable, List, Optional

from src.core.hub import ComponentHub
from src.core.info import ComponentSourceDescriptor, ComponentInfo
from src.core.interface import ComponentInterface
from src.core.loader import ComponentLoader

=======
import logging
from typing import Callable, List, Optional

from src.core.hub import ComponentHub
from src.core.info import ComponentSourceDescriptor, ComponentInfo, ComponentMeta
from src.core.interface import ComponentInterface
from src.core.loader import ComponentLoader

logger = logging.getLogger(__name__)

>>>>>>> da731b0 (支持组件间依赖识别与阻断组件)

class ComponentSystem:
    def __init__(self):
        self.hub = ComponentHub()
        self.loader = ComponentLoader()
        self.component_infos = self.hub.component_infos

    def create_manager(self, name: str, specs: List[Callable[..., type]] = []):
        self.hub.create_manager(name, specs)

    def get_manager(self, name: str):
        return self.hub.get_manager(name)

    def destroy_manager(self, name: str):
        self.hub.destroy_manager(name)

    def get_components(self, manager_name: str) -> set[ComponentInterface]:
        return self.hub.get_components(manager_name)

    def get_components_id(self, manager_name: str) -> set[str]:
        return self.hub.get_components_id(manager_name)

    def get_component_info(self, component_id: str) -> Optional[ComponentInfo]:
        return self.hub.get_component_info(component_id)
<<<<<<< HEAD
=======

    def check_component_dependencies(self, meta: ComponentMeta) -> bool:
        missing = [
            dependency
            for dependency in meta.dependencies.components
            if dependency not in self.component_infos
        ]
        if missing:
            logger.error(
                "Component '%s' cannot be loaded because missing component dependencies: %s",
                meta.id,
                missing,
            )
            return False
        return True
>>>>>>> da731b0 (支持组件间依赖识别与阻断组件)

    def del_component(self, component_id: str):
        self.hub.del_component(component_id)

    def clear_components(self):
        self.hub.clear_components()

    def shutdown(self):
        self.hub.shutdown()

    def bind_spec_to_manager(self, name: str, spec: Callable[..., type]):
        self.hub.bind_spec_to_manager(name, spec)

    def get_spec_hook(self, name: str):
        return self.hub.get_spec_hook(name)

    def get_impl_hook(self, name: str):
        return self.hub.get_impl_hook(name)

    def execute_hook(self, manager_name: str, hook_name: str, *args, **kwargs):
        return self.hub.execute_hook(manager_name, hook_name, *args, **kwargs)

    def load_component_module(self, component_descriptor: ComponentSourceDescriptor):
        return self.loader.load_component_module(component_descriptor)

    def load_component(self, module):
        return self.loader.load_component(module, self)

    def register_component_to_system(self, component_info: ComponentInfo):
        self.hub.register_component_info(component_info)

    def register_component(self, component_descriptor: ComponentSourceDescriptor):
<<<<<<< HEAD
        module = self.loader.load_component_module(component_descriptor)
        component_info = self.loader.load_component(module, self)
        if component_info:
            self.hub.register_component_info(component_info)
        return component_info
=======
        try:
            module = self.loader.load_component_module(component_descriptor)
            component_info = self.loader.load_component(module, self)
            if component_info:
                self.hub.register_component_info(component_info)
            return component_info
        except Exception:
            logger.error(
                "Unexpected failure registering component descriptor %s",
                component_descriptor,
                exc_info=True,
            )
            return None
>>>>>>> da731b0 (支持组件间依赖识别与阻断组件)

    def normalize_to_init_path(self, p: str):
        return self.loader.normalize_to_init_path(p)

    def parse_toml_meta(self, file: str):
        return self.loader.parse_toml_meta(file)
