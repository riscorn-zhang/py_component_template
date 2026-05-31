# 程序所需的全局命名空间（大部分由程序初始化时生成）
import src.vars.infos as infos

import platformdirs
import os

APP_DIRS = platformdirs.PlatformDirs(appname=infos.APP_NAME, appauthor=infos.APP_AUTHOR)

for dir in [APP_DIRS.user_log_dir]:
    os.makedirs(dir, exist_ok=True)

LOGGING_DICT = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "filename": f"{APP_DIRS.user_log_dir}/app.log",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },
    },
}

APP_CURRENT_DIR = ""


def runtime_var_initialization(file_global_var):
    global APP_CURRENT_DIR
    APP_CURRENT_DIR = os.path.dirname(os.path.abspath(file_global_var))


__all__ = ["APP_DIRS", "LOGGING_DICT"]
