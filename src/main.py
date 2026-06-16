import logging

from src.core.system import ComponentSystem

from src.sugar import temperory_placeholder
from src.vars import configs, infos, runtimes, functions
from src.vars.debug import EXC_INFO
from src.core.info import ComponentSourceDescriptor

logger = logging.getLogger(__name__)

runtimes.runtime_var_initialization(__file__)
runtimes.flush_logging_config()

system = ComponentSystem()

try:
    for manager, specs in configs.INIT_MANAGERS.items():
        system.hub.create_manager(manager, specs)

    # for component_location in configs.INIT_COMPONENTS:
    #     try:
    #         system.register_component(
    #             ComponentSourceDescriptor(
    #                 type="package", location=functions.absolute_path(component_location)
    #             )
    #         )
    #     except Exception:
    #         logger.error(
    #             "Failed to register component %s",
    #             component_location,
    #             exc_info=EXC_INFO,
    #         )

    system.batch_register_components(
        [
            ComponentSourceDescriptor(
                type="package", location=functions.absolute_path(component_location)
            )
            for component_location in configs.INIT_COMPONENTS
        ]
    )

    try:
        system.execute_hook("app", "entry")
    except Exception:
        logger.critical("Application entry hook failed", exc_info=EXC_INFO)

except Exception:
    logger.critical(
        "Unexpected fatal error during application startup", exc_info=EXC_INFO
    )

finally:
    temperory_placeholder(configs, infos, runtimes)
