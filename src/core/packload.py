import importlib.util
import importlib.machinery
import sys
from pathlib import Path

from src.vars.functions import generate_anoymous_pkg_name


def load_package_anonymously(package_path):
    """
    匿名加载一个包目录（包含 __init__.py 文件）并支持包内相对导入。
    加载过程中会暂时使用一个随机包名注册到 sys.modules
    加载完成后删除 sys.modules 中的相关条目，返回包模块对象。
    :param package_path: 包的目录路径，如 '/path/to/package_a'
    :return: 包的模块对象（相当于 import package_a 得到的对象）
    """
    package_path = Path(package_path).resolve()
    init_file = package_path

    pkg_name = generate_anoymous_pkg_name()
    spec = importlib.util.spec_from_file_location(
        pkg_name,
        init_file,
        loader=importlib.machinery.SourceFileLoader(pkg_name, str(init_file)),
        submodule_search_locations=[str(package_path)],
    )

    if not spec or not spec.loader:
        raise ImportError(f"Failed to load package: {package_path}")

    module = importlib.util.module_from_spec(spec)
    old_modules = set(sys.modules.keys())
    sys.modules[pkg_name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        new_modules = set(sys.modules.keys()) - old_modules
        for name in list(new_modules):
            if name == pkg_name or name.startswith(pkg_name + "."):
                sys.modules.pop(name, None)
    return module
