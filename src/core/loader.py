from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Any
import importlib
import logging
import tomllib
import importlib.machinery
import sys
from pathlib import Path
from importlib import util

from src.vars.functions import generate_anoymous_pkg_name


from src.core.info import (
    ComponentSourceDescriptor,
    ComponentMeta,
    ComponentInfo,
    ComponentDependencies,
)
from src.vars.debug import EXC_INFO

if TYPE_CHECKING:
    from src.core.system import ComponentSystem

logger = logging.getLogger(__name__)


class InitFileNotFoundError(FileNotFoundError):
    pass


class ComponentLoader:
    "组件加载器, 解析成ComponentInfo对象"

    def _load_package_anonymously(self, package_path):
        """
        匿名加载一个包目录（包含 __init__.py 文件）并支持包内相对导入。
        加载过程中会暂时使用一个随机包名注册到 sys.modules
        加载完成后删除 sys.modules 中的相关条目，返回包模块对象。
        :param package_path: 包的目录路径，如 '/path/to/package_a'
        :return: 包的模块对象（相当于 import package_a 得到的对象）
        """
        package_path = Path(package_path).resolve()
        init_file = package_path

        pkg_name = generate_anoymous_pkg_name()
        spec = util.spec_from_file_location(
            pkg_name,
            init_file,
            loader=importlib.machinery.SourceFileLoader(pkg_name, str(init_file)),
            submodule_search_locations=[str(package_path)],
        )

        if not spec or not spec.loader:
            raise ImportError(f"Failed to load package: {package_path}")

        module = util.module_from_spec(spec)
        old_modules = set(sys.modules.keys())
        sys.modules[pkg_name] = module
        try:
            spec.loader.exec_module(module)
        finally:
            new_modules = set(sys.modules.keys()) - old_modules
            for name in list(new_modules):
                if name == pkg_name or name.startswith(pkg_name + "."):
                    sys.modules.pop(name, None)
        return module

    def _parse_toml_meta(self, file: str) -> ComponentMeta:
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

    def _normalize_to_init_path(self, p: str) -> Path:
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
                return self._load_package_anonymously(
                    self._normalize_to_init_path(name)
                )
            else:
                logger.error(
                    "Unknown component type %s for descriptor %s",
                    component_descriptor.type,
                    name,
                )
                return None
        except Exception:
            logger.error(
                "Failed to import component module %s: %s",
                name,
                exc_info=EXC_INFO,
            )
            return None

    def load_component_meta(self, module):
        return self._parse_toml_meta(str(Path(module.__file__).parent / "meta.toml"))

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
            meta = self.load_component_meta(module)
            if not system._check_component_dependencies(meta):
                return None
            return ComponentInfo(
                meta=meta,
                instance=module.component(system)(),
            )
        except TypeError:
            logger.error(
                "Component %s has invalid component function signature: %s",
                name,
                exc_info=EXC_INFO,
            )
            return None
        except Exception:
            logger.error(
                "Failed to instantiate component %s: %s",
                name,
                exc_info=EXC_INFO,
            )
            return None
