from typing import Type
import logging
from pathlib import Path

from src.core.system import ComponentSystem
from src.core.interface import ComponentInterface


logger = logging.getLogger(__name__)


def meta_path() -> Path:
    return Path(__file__).parent / "meta.toml"


def component(system: ComponentSystem) -> Type[ComponentInterface]:
    hookimpl = system.get_impl_hook("app")

    class ServiceMainComponent(ComponentInterface):
        @hookimpl
        def start_service(self):
            logger.info("Starting service daemon...")
            logger.info("Daemon is always running.")

    return ServiceMainComponent
