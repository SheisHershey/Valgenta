"""
tools 包：工具集

使用 LangChain 的 @tool 装饰器定义工具，本模块提供自动发现机制，
扫描 tools 包下的所有子模块，收集被 @tool 装饰的函数。
"""
import importlib
import pkgutil
from pathlib import Path
from typing import List

from langchain_core.tools import BaseTool

# 不参与工具发现的模块名
_EXCLUDED = {"base", "decorator", "schema", "_register", "result"}


def get_tools() -> List[BaseTool]:
    """
    自动发现并返回所有工具实例

    扫描当前包目录下的 .py 文件，导入每个模块，
    收集其中所有 BaseTool 实例（由 @tool 装饰器生成）。

    Returns:
        List[BaseTool]: 所有已注册的工具列表
    """
    tools: List[BaseTool] = []
    package_dir = Path(__file__).parent

    for module_info in pkgutil.iter_modules([str(package_dir)]):
        name = module_info.name
        if name in _EXCLUDED or name.startswith("_"):
            continue

        module = importlib.import_module(f"tools.{name}")
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, BaseTool):
                tools.append(attr)

    return tools
