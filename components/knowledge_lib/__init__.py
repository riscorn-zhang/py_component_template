from typing import Type

from src.core.system import ComponentSystem
from src.core.interface import ComponentInterface

import logging

logger = logging.getLogger(__name__)


def component(system: ComponentSystem) -> Type[ComponentInterface]:
    hookimpl = system.get_impl_hook("app")

    class Component(ComponentInterface):
        def on_del(self):
            pass

        def on_init(self):
            pass

        @hookimpl
        def entry(self):
            print("This is the knowledge library component.")

    return Component
