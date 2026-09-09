"""
兼容入口：委托给 langchainmain 主模块

langchainmain 是框架的主入口，本文件仅作向后兼容的转发。
推荐直接运行：python langchainmain.py
"""
from langchainmain import main

if __name__ == "__main__":
    main()
