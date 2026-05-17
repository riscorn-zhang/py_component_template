from typing import List, Type
import logging

from src.core.system import ComponentSystem
from src.core.interface import ComponentInterface


logger = logging.getLogger(__name__)


def component(system: ComponentSystem) -> Type[ComponentInterface]:
    hookimpl = system.get_impl_hook("app")

    class ServiceMainComponent(ComponentInterface):
        @property
        def id(self) -> str:
            return "app.daemon"

        @property
        def name(self) -> str:
            return "Service Daemon"

        @property
        def belong_managers(self) -> List[str]:
            return ["app"]

        def on_del(self):
            pass

        def on_init(self):
            pass

        @hookimpl
        def start_service(self):
            logger.info("Starting service daemon...")
            logger.info("Daemon is always running.")

    return ServiceMainComponent
