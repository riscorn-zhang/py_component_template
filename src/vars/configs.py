# 用户配置的全局命名空间
from src.specs.app import spec as app_spec

INIT_COMPONENTS = [
    "src/components/entry",
    "src/components/service",
    "src/components/client",
]

INIT_MANAGERS = {
    "app": [app_spec],
}
