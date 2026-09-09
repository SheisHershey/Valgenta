"""
天气查询工具
返回指定城市的天气信息（模拟数据）
"""
from langchain_core.tools import tool


@tool
def weather(city: str) -> str:
    """查询城市天气"""
    data = {
        "东京": "小雨 22℃",
        "北京": "晴天 25℃",
        "上海": "多云 28℃",
    }
    return data.get(city, "未知天气")
