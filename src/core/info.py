from pydantic import BaseModel, Field
from dataclasses import dataclass
from typing import Literal, List
from src.core.interface import ComponentInterface

ComponentType = Literal["module", "builtin", "wheel", "package"]


class ComponentSourceDescriptor(BaseModel):
    """组件描述符类, 但是准备用 importlib.machinery.ModuleSpec 替代这个数据结构"""

    type: ComponentType
    location: str


class ComponentDependencies(BaseModel):
    python: List[str] = Field(default_factory=list)
    components: List[str] = Field(default_factory=list)


class ComponentMeta(BaseModel):
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
