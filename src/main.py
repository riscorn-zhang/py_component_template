from src.core.system import ComponentSystem
from src.specs.app import spec as app_spec

from src.sugar import temperory_placeholder
from src.vars.vars import configs, infos, runtimes
from src.core.descriptor import ComponentDescriptor

system = ComponentSystem()
system.create_manager("app", [app_spec])
system.register_component(ComponentDescriptor(type="builtin", location="entry"))
system.get_manager("app").hook.entry()

temperory_placeholder(configs, infos, runtimes)
