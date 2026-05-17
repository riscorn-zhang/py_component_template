from src.core.system import ComponentSystem


def spec(system: ComponentSystem):
    hookspec = system.get_spec_hook("app")

    class AppSpec:
        @hookspec
        def entry(self):
            pass

        @hookspec
        def start_service(self):
            pass

        @hookspec
        def start_client(self):
            pass

    return AppSpec
