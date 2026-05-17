from pydantic import BaseModel
from typing import Literal

ComponentType = Literal["module", "builtin", "wheel", "package"]


class ComponentDescriptor(BaseModel):
    """组件描述符类"""

    type: ComponentType
    location: str
