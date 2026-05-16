from typing import List

from src.core.system import ComponentSystem


def spec(system: ComponentSystem):
    hookspec = system.get_spec_hook("app")

    class AppSpec:
        @hookspec
        def start_app(self, argv: List[str]):
            pass

    return AppSpec
