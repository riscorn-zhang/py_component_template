from pydantic import BaseModel
from typing import Literal

ComponentType = Literal["module", "builtin", "file", "package"]


class ComponentDescriptor(BaseModel):
    """组件描述符类"""

    type: ComponentType
    location: str
