from dataclasses import dataclass, field
from typing import Literal, List
from src.core.interface import ComponentInterface

ComponentType = Literal["module", "builtin", "wheel", "package"]


@dataclass
class ComponentSourceDescriptor:
    """组件描述符类, 但是准备用 importlib.machinery.ModuleSpec 替代这个数据结构"""

    type: ComponentType
    location: str


@dataclass
class ComponentDependencies:
    libraries: List[str] = field(default_factory=list)
    components: List[str] = field(default_factory=list)


@dataclass
class ComponentMeta:
    id: str
    name: str
    version: str
    description: str | None
    belong_managers: List[str]
    dependencies: ComponentDependencies


@dataclass
class ComponentInfo:
    meta: ComponentMeta
    instance: ComponentInterface
