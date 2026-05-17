from abc import ABC, abstractmethod
from src.sugar import temperory_placeholder


class ComponentInterface:
    def on_init(self):
        pass

    def on_del(self):
        pass


temperory_placeholder(ABC, abstractmethod)
