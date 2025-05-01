"""
交互式配置向导模块
"""

import os
import sys


def print_header(title):
    """打印配置向导标题"""
    width = 60
    print("\n" + "=" * width)
    print(f"{title:^{width}}")
    print("=" * width + "\n")


def get_input(prompt, default=None, validator=None, choices=None):
    """获取用户输入，支持默认值和验证"""
    if default is not None:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    while True:
        user_input = input(prompt).strip()
        
        # 用户未输入，使用默认值
        if not user_input and default is not None:
            return default
        
        # 如果有选项限制，验证输入
        if choices and user_input not in choices:
            print(f"输入错误！请从以下选项中选择: {', '.join(choices)}")
            continue
        
        # 如果有验证函数，验证输入
        if validator and not validator(user_input):
            continue
            
        return user_input


def number_choice(choices, prompt):
    """显示编号选项并获取用户选择"""
    print(prompt)
    for i, choice in enumerate(choices, 1):
        print(f"  {i}. {choice}")
    
    while True:
        try:
            choice = input("[1]: ").strip()
            if not choice:
                return choices[0]  # 默认第一个选项
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(choices):
                return choices[choice_num - 1]
            else:
                print(f"请输入 1-{len(choices)} 之间的数字!")
        except ValueError:
            print("请输入有效数字!")


def validate_url(url):
    """验证URL格式"""
    if not url.startswith(("http://", "https://")):
        print("URL 必须以 http:// 或 https:// 开头!")
        return False
    return True


def run_config_wizard(config):
    """运行交互式配置向导"""
    # 检查当前终端环境支持的语言
    is_chinese_supported = True
    try:
        print("正在检查终端是否支持中文...")
        sys.stdout.write("测试中文支持\n")
        sys.stdout.flush()
    except UnicodeEncodeError:
        is_chinese_supported = False
    
    # 清屏
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # 初始化语言界面文字
    if is_chinese_supported:
        language_choices = ["English", "中文"]
        title = "Viby 配置向导 / Viby Configuration Wizard"
        language_prompt = "请选择界面语言 / Please select interface language:"
    else:
        language_choices = ["English", "Chinese"]
        title = "Viby Configuration Wizard"
        language_prompt = "Please select interface language:"
    
    print_header(title)
    
    # 语言选择
    language = number_choice(language_choices, language_prompt)
    if language in ["中文", "Chinese"]:
        config.language = "zh-CN"
        print("\n已选择中文界面")
        
        # 中文界面提示
        model_prompt = "选择默认模型"
        temp_prompt = "温度参数 (0.0-1.0)"
        max_tokens_prompt = "最大令牌数"
        api_url_prompt = "API 基础URL"
        api_timeout_prompt = "API 超时时间(秒)"
        api_key_prompt = "API 密钥(如需)"
        
        save_prompt = "配置已保存至"
        continue_prompt = "按 Enter 键继续..."
    else:
        config.language = "en-US"
        print("\nSelected English interface")
        
        # 英文界面提示
        model_prompt = "Select default model"
        temp_prompt = "Temperature (0.0-1.0)"
        max_tokens_prompt = "Maximum tokens"
        api_url_prompt = "API base URL"
        api_timeout_prompt = "API timeout (seconds)"
        api_key_prompt = "API key (if needed)"
        
        save_prompt = "Configuration saved to"
        continue_prompt = "Press Enter to continue..."
    
    print("\n" + "-" * 60)
    
    # 模型选择
    models = ["qwen3:30b", "qwen3:7b", "llama3:70b", "llama3:8b", "mistral:7b", "custom"]
    chosen_model = number_choice(models, model_prompt)
    if chosen_model == "custom":
        config.model = get_input(f"{model_prompt} (custom)", config.model)
    else:
        config.model = chosen_model
    
    # 温度设置
    while True:
        temp = get_input(temp_prompt, str(config.temperature))
        try:
            temp_value = float(temp)
            if 0.0 <= temp_value <= 1.0:
                config.temperature = temp_value
                break
            print("温度值必须在 0.0 到 1.0 之间!")
        except ValueError:
            print("请输入有效的小数!")
    
    # 最大令牌数
    while True:
        max_tokens = get_input(max_tokens_prompt, str(config.max_tokens))
        try:
            tokens_value = int(max_tokens)
            if tokens_value > 0:
                config.max_tokens = tokens_value
                break
            print("令牌数必须大于 0!")
        except ValueError:
            print("请输入有效的整数!")
    
    # API URL
    config.base_url = get_input(api_url_prompt, config.base_url, validator=validate_url)
    
    # API 超时
    while True:
        timeout = get_input(api_timeout_prompt, str(config.api_timeout))
        try:
            timeout_value = int(timeout)
            if timeout_value > 0:
                config.api_timeout = timeout_value
                break
            print("超时时间必须大于 0!")
        except ValueError:
            print("请输入有效的整数!")
    
    # API Key
    config.api_key = get_input(api_key_prompt, config.api_key or "")
    
    # 保存配置
    config.save_config()
    
    print("\n" + "-" * 60)
    print(f"{save_prompt}: {config.config_path}")
    input(f"\n{continue_prompt}")
    return config
