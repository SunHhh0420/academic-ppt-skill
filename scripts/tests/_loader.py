"""测试辅助：按文件路径加载 scripts 下的单文件脚本模块。

脚本仅用标准库、未打包为 Python 包，这里用 importlib 按路径加载，
使 unittest 可以直接调用其顶层函数。
"""

import importlib.util
import pathlib

SCRIPTS_DIR = pathlib.Path(__file__).resolve().parent.parent


def load(module_name: str):
    path = SCRIPTS_DIR / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
