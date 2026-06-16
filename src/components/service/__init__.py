from typing import Type
import logging

from src.core.system import ComponentSystem
from src.core.interface import ComponentInterface
from src.vars import runtimes


logger = logging.getLogger(__name__)


def component(system: ComponentSystem) -> Type[ComponentInterface]:
    hookimpl = system.hub.get_impl_hook("app")

    class ServiceMainComponent(ComponentInterface):
        @hookimpl
        def start_service(self):
            print(runtimes.LOGGING_DICT["handlers"]["console"]["level"])
            logger.info("Starting service daemon...")
            logger.info("Daemon is always running.")

    return ServiceMainComponent
