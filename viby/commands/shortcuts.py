#!/usr/bin/env python3
"""
Viby 键盘快捷键命令
处理快捷键的安装和管理
"""

import argparse
from typing import Optional, Any

from viby.utils.keyboard_shortcuts import install_shortcuts, detect_shell
from viby.locale import get_text

class ShortcutsCommand:
    """处理快捷键安装和管理的命令"""
    
    def __init__(self):
        """初始化快捷键命令"""
        pass
    
    def execute(self, subcommand: Optional[str] = None, args: Any = None) -> int:
        """
        执行快捷键命令
        
        Args:
            subcommand: 不再使用
            args: 命令行参数
            
        Returns:
            命令执行的退出码
        """
        # 获取shell类型，优先使用参数指定的shell
        shell = getattr(args, "shell", None) if args else None
        
        # 如果没有指定shell，打印自动检测提示
        if not shell:
            detected_shell = detect_shell()
            if detected_shell:
                print(f"{get_text('SHORTCUTS', 'auto_detect_shell')}: {detected_shell}")
            else:
                print(get_text('SHORTCUTS', 'auto_detect_failed'))
        
        # 安装快捷键
        result = install_shortcuts(shell)
        
        # 显示安装结果
        self._print_result(result)
        
        # 根据操作状态设置退出码
        return 0 if result["status"] in ["success", "info"] else 1
    
    def _print_result(self, result: dict) -> None:
        """
        打印操作结果
        
        Args:
            result: 操作结果字典
        """
        # 根据状态使用不同颜色
        if result["status"] == "success":
            status_color = "\033[92m"  # 绿色
        elif result["status"] == "info":
            status_color = "\033[94m"  # 蓝色
        else:
            status_color = "\033[91m"  # 红色
        
        reset_color = "\033[0m"
        
        print(f"{status_color}[{result['status'].upper()}]{reset_color} {result['message']}")
        
        # 如果需要用户操作，显示提示
        if "action_required" in result:
            print(f"\n{get_text('SHORTCUTS', 'action_required').format(result['action_required'])}")
        
        if result["status"] == "success":
            print(f"\n{get_text('SHORTCUTS', 'activation_note')}") 