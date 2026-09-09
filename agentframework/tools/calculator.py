"""
计算器工具
使用 langchain_core.tools.tool 装饰器定义工具

@tool 装饰器会自动完成：
1. 从函数签名和类型注解生成 JSON Schema
2. 将函数包装为 StructuredTool 实例
3. 提取 docstring 作为工具描述
"""
from langchain_core.tools import tool


@tool
def calculator(a: int, b: int) -> int:
    """计算两个数字的和"""
    return a + b
