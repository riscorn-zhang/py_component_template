from src.core.system import ComponentSystem
from src.specs.app import spec as app_spec

from src.sugar import temperory_placeholder
from src.vars.vars import configs, infos, runtimes
from src.core.info import ComponentSourceDescriptor
from src.vars.functions import absolute_path

runtimes.runtime_var_initialization(__file__)

system = ComponentSystem()
system.create_manager("app", [app_spec])
# system.register_component(ComponentSourceDescriptor(type="builtin", location="entry"))
system.register_component(
    ComponentSourceDescriptor(
        type="package", location=absolute_path("src/components/entry")
    )
)
# system.register_component(
#     ComponentSourceDescriptor(
#         type="package", location=absolute_path("components/knowledge_lib")
#     )
# )
system.get_manager("app").hook.entry()

temperory_placeholder(configs, infos, runtimes)
