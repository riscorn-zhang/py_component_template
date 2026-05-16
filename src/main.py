from src.core.system import ComponentSystem
from src.core.specs.app import spec as app_spec

from src.sugar import temperory_placeholder
from src.public_namespace import globals, configs
from src.core.descriptor import ComponentDescriptor

import sys

system = ComponentSystem()
system.create_manager("app", [app_spec])
system.register_component(
    ComponentDescriptor(type="module", location="src.core.components.entry.component")
)
system.get_manager("app").hook.start_app(argv=sys.argv)

temperory_placeholder(globals, configs)
