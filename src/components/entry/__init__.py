from typing import Type

from src.core.system import ComponentSystem
from src.core.interface import ComponentInterface
from src.core.info import ComponentSourceDescriptor
from src.vars import runtimes

import sys
import logging
import logging.config

logger = logging.getLogger(__name__)


def component(system: ComponentSystem) -> Type[ComponentInterface]:
    hookimpl = system.get_impl_hook("app")

    class EntryComponent(ComponentInterface):
        def on_del(self):
            pass

        def on_init(self):
            pass

        @hookimpl
        def entry(self):
            logging.config.dictConfig(runtimes.LOGGING_DICT)

            logger.debug("")
            logger.debug("=========Start New Process=========")
            logger.debug("")

            if len(sys.argv) > 1:
                if sys.argv[1] == "service":
                    self.service()
                elif sys.argv[1] == "client":
                    self.client()
                else:
                    logger.error(f"Unknown argument: {sys.argv[1]}")
            else:
                self.service()
                self.client()

            print(system.component_infos["app.daemon"])

            text = ""

            while True:
                text = input("DEBUG >>> ")
                if text == "exit":
                    break

                try:
                    print(eval(text))
                except Exception:
                    pass

                try:
                    exec(text)
                except Exception as e:
                    print(e.__class__.__name__, e)

        def service(self):
            system.register_component(
                ComponentSourceDescriptor(type="builtin", location="service")
            )
            system.get_manager("app").hook.start_service()

        def client(self):
            runtimes.LOGGING_DICT["handlers"]["console"]["level"] = "CRITICAL"
            logging.config.dictConfig(runtimes.LOGGING_DICT)

            system.register_component(
                ComponentSourceDescriptor(type="builtin", location="client")
            )
            system.get_manager("app").hook.start_client()

    return EntryComponent
