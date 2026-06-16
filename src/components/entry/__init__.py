from typing import Type

from src.core.system import ComponentSystem
from src.core.interface import ComponentInterface
from src.vars import runtimes

import logging
import argparse
import logging.config

logger = logging.getLogger(__name__)


def component(system: ComponentSystem) -> Type[ComponentInterface]:
    hookimpl = system.hub.get_impl_hook("app")

    class EntryComponent(ComponentInterface):
        def on_del(self):
            pass

        def on_init(self):
            pass

        @hookimpl
        def entry(self):
            parser = argparse.ArgumentParser(
                prog="xxx", description="E.g. daemon / client"
            )

            subparsers = parser.add_subparsers(dest="command")
            subparsers.add_parser("daemon", help="启动后台服务")
            subparsers.add_parser("client", help="运行客户端")

            args = parser.parse_args()

            if args.command == "daemon":
                self.service()
            elif args.command == "client":
                self.client()
            else:
                self.service()
                self.client()

        def service(self):
            system.execute_hook("app", "start_service")

        def client(self):
            runtimes.LOGGING_DICT["handlers"]["console"]["level"] = "CRITICAL"
            runtimes.flush_logging_config()

            logging.config.dictConfig(runtimes.LOGGING_DICT)

            system.execute_hook("app", "start_client")

    return EntryComponent
