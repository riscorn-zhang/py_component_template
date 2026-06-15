from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Any
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
from src.core.packload import load_package_anonymously

if TYPE_CHECKING:
    from src.core.system import ComponentSystem

logger = logging.getLogger(__name__)


class InitFileNotFoundError(FileNotFoundError):
    pass


class ComponentLoader:
    def parse_toml_meta(self, file: str) -> ComponentMeta:
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
            libraries=list(deps_raw.get("libraries", []) or []),
            components=list(deps_raw.get("components", []) or []),
        )

        if dependencies.libraries:
            logger.warning(
                "Component %s declares library dependencies but library resolution is not handled yet: %s",
                raw["id"],
                dependencies.libraries,
            )

        return ComponentMeta(
            id=raw["id"],
            name=raw["name"],
            version=raw["version"],
            description=raw.get("description"),
            belong_managers=list(raw.get("belong_managers", []) or []),
            dependencies=dependencies,
        )

    def normalize_to_init_path(self, p: str) -> Path:
        path = Path(p).resolve()
        if not path.exists():
            raise FileNotFoundError(f"路径不存在: {path}")
        if path.is_dir():
            init_path = path / "__init__.py"
            if not init_path.is_file():
                raise InitFileNotFoundError(f"目录中没有 __init__.py: {path}")
            return init_path
        if path.name != "__init__.py":
            raise InitFileNotFoundError(f"文件不是 __init__.py: {path}")
        return path

    def load_component_module(self, component_descriptor: ComponentSourceDescriptor):
        name = component_descriptor.location

        try:
            if component_descriptor.type == "module":
                return importlib.import_module(name)
            elif component_descriptor.type == "builtin":
                return importlib.import_module(f"src.components.{name}")
            elif component_descriptor.type == "wheel":
                logger.error("Wheel package loading is not supported yet: %s", name)
                return None
            elif component_descriptor.type == "package":
                return load_package_anonymously(self.normalize_to_init_path(name))
            else:
                logger.error(
                    "Unknown component type %s for descriptor %s",
                    component_descriptor.type,
                    name,
                )
                return None
        except Exception as e:
            logger.error(
                "Failed to import component module %s: %s",
                name,
                e,
                exc_info=True,
            )
            return None

    def load_component(
        self, module, system: "ComponentSystem"
    ) -> Optional[ComponentInfo]:
        if module is None:
            return None

        name = module.__name__
        if not hasattr(module, "component"):
            logger.error("模块 %s 没有 component 函数", name)
            return None

        try:
            meta = self.parse_toml_meta(
                str(Path(str(module.__file__)).parent / "meta.toml")
            )
            if not system.check_component_dependencies(meta):
                return None
            return ComponentInfo(
                meta=meta,
                instance=module.component(system)(),
            )
        except TypeError as e:
            logger.error(
                "Component %s has invalid component function signature: %s",
                name,
                e,
                exc_info=True,
            )
            return None
        except Exception as e:
            logger.error(
                "Failed to instantiate component %s: %s",
                name,
                e,
                exc_info=True,
            )
            return None
