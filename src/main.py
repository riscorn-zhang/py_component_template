import logging

from src.core.system import ComponentSystem

from src.sugar import temperory_placeholder
from src.vars import configs, infos, runtimes, functions
from src.core.info import ComponentSourceDescriptor

logger = logging.getLogger(__name__)

runtimes.runtime_var_initialization(__file__)

system = ComponentSystem()

try:
    for manager, specs in configs.INIT_MANAGERS.items():
        system.create_manager(manager, specs)

    for component_location in configs.INIT_COMPONENTS:
        try:
            system.register_component(
                ComponentSourceDescriptor(
                    type="package", location=functions.absolute_path(component_location)
                )
            )
        except Exception:
            logger.error(
                "Failed to register component %s",
                component_location,
                exc_info=True,
            )

    try:
        system.get_manager("app").hook.entry()
    except Exception:
        logger.critical("Application entry hook failed", exc_info=True)

except Exception:
    logger.critical("Unexpected fatal error during application startup", exc_info=True)

finally:
    temperory_placeholder(configs, infos, runtimes)
