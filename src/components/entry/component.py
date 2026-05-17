from typing import List

from src.core.system import ComponentSystem
from src.core.interface import ComponentInterface

from typing import Type


def component(system: ComponentSystem) -> Type[ComponentInterface]:
    hookimpl = system.get_impl_hook("app")

    class EntryComponent(ComponentInterface):
        def dependencies(self) -> List[str]:
            return []

        def id(self) -> str:
            return "entry"

        def name(self) -> str:
            return "Entry"

        def belong_managers(self) -> List[str]:
            return ["app"]

        def on_del(self):
            pass

        def on_init(self):
            pass

        @hookimpl
        def start_app(self, argv: List[str]):
            print("Starting app...")
            print("Arguments:", argv)

    return EntryComponent
