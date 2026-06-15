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

        if component_descriptor.type == "module":
            return importlib.import_module(name)
        elif component_descriptor.type == "builtin":
            return importlib.import_module(f"src.components.{name}")
        elif component_descriptor.type == "wheel":
            raise NotImplementedError("Wheel Package Loading is not supported yet")
        elif component_descriptor.type == "package":
            return load_package_anonymously(self.normalize_to_init_path(name))
        else:
            raise RuntimeError(f"未知的组件类型: {component_descriptor.type}")

    def load_component(
        self, module, system: "ComponentSystem"
    ) -> Optional[ComponentInfo]:
        name = module.__name__
        if not hasattr(module, "component"):
            raise RuntimeError(f"模块 {name} 没有 component 函数")

        try:
            return ComponentInfo(
                meta=self.parse_toml_meta(
                    str(Path(str(module.__file__)).parent / "meta.toml")
                ),
                instance=module.component(system)(),
            )
        except TypeError as e:
            raise RuntimeError(
                f"模块 {name} 的 component 或 meta_path 函数结构不匹配: {e}"
            )
        except Exception as e:
            raise RuntimeError(f"加载模块 {name} 的 component 函数执行错误: {e}")
