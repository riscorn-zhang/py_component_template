from abc import ABC, abstractmethod
from typing import Any, List


class ComponentInterface(ABC):
    @property
    @abstractmethod
    def id(self) -> str:
        """组件唯一标识符 (强制实现)"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """组件显示名称 (强制实现)"""
        pass

    @property
    @abstractmethod
    def belong_managers(self) -> List[str]:
        """组件所属管理器 (强制实现)"""
        pass

    @property
    def dependencies(self) -> List[str]:
        """组件依赖列表 (可选实现，默认为空)"""
        return []

    @abstractmethod
    def on_init(self):
        pass

    @abstractmethod
    def on_del(self):
        pass
