"""
Interactive configuration wizard module
"""

import os
import sys
import shutil
from viby.locale import get_text, init_text_manager
from viby.utils.formatting import print_separator


def print_header(title):
    """打印配置向导标题"""
    print()
    print_separator("=")
    print(f"{title:^{shutil.get_terminal_size().columns}}")
    print_separator("=")
    print()


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
                print(get_text("CONFIG_WIZARD", "number_range_error").format(len(choices)))
        except ValueError:
            print(get_text("CONFIG_WIZARD", "invalid_number"))


def validate_url(url):
    """验证URL格式"""
    if not url.startswith(("http://", "https://")):
        print(get_text("CONFIG_WIZARD", "url_error"))
        return False
    return True


def run_config_wizard(config):
    """运行交互式配置向导"""
    # Check Chinese support in current terminal
    is_chinese_supported = True
    try:
        print(get_text("CONFIG_WIZARD", "checking_chinese"))
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
        init_text_manager(config)
        print("\n" + get_text("CONFIG_WIZARD", "selected_language"))
        
    else:
        config.language = "en-US"
        init_text_manager(config)
        print("\n" + get_text("CONFIG_WIZARD", "selected_language"))
        
    model_prompt = get_text("CONFIG_WIZARD", "model_prompt")
    temp_prompt = get_text("CONFIG_WIZARD", "temperature_prompt")
    max_tokens_prompt = get_text("CONFIG_WIZARD", "max_tokens_prompt")
    api_url_prompt = get_text("CONFIG_WIZARD", "api_url_prompt")
    api_timeout_prompt = get_text("CONFIG_WIZARD", "api_timeout_prompt")
    api_key_prompt = get_text("CONFIG_WIZARD", "api_key_prompt")
    save_prompt = get_text("CONFIG_WIZARD", "config_saved")
    continue_prompt = get_text("CONFIG_WIZARD", "continue_prompt")
    
    print()
    print_separator()

    # API URL
    config.base_url = get_input(api_url_prompt, config.base_url, validator=validate_url)
    
    # API Key
    config.api_key = get_input(api_key_prompt, config.api_key or "")

    # 模型选择
    models = [
    get_text("CONFIG_WIZARD", "model_qwen3"),
    get_text("CONFIG_WIZARD", "model_deepseek"),
    get_text("CONFIG_WIZARD", "model_gpt4o"),
    get_text("CONFIG_WIZARD", "model_custom")
]
    chosen_model = number_choice(models, model_prompt)
    if chosen_model == get_text("CONFIG_WIZARD", "model_custom"):
        config.model = get_input(f"{model_prompt} ({get_text('CONFIG_WIZARD', 'model_custom')})", config.model)
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
            print(get_text("CONFIG_WIZARD", "temperature_range"))
        except ValueError:
            print(get_text("CONFIG_WIZARD", "invalid_decimal"))
    
    # 最大令牌数
    while True:
        max_tokens = get_input(max_tokens_prompt, str(config.max_tokens))
        try:
            tokens_value = int(max_tokens)
            if tokens_value > 0:
                config.max_tokens = tokens_value
                break
            print(get_text("CONFIG_WIZARD", "tokens_positive"))
        except ValueError:
            print(get_text("CONFIG_WIZARD", "invalid_integer"))
    
    
    # API 超时
    while True:
        timeout = get_input(api_timeout_prompt, str(config.api_timeout))
        try:
            timeout_value = int(timeout)
            if timeout_value > 0:
                config.api_timeout = timeout_value
                break
            print(get_text("CONFIG_WIZARD", "timeout_positive"))
        except ValueError:
            print(get_text("CONFIG_WIZARD", "invalid_integer"))
    
    
    # 保存配置
    config.save_config()
    
    print()
    print_separator()
    print(f"{save_prompt}: {config.config_path}")
    input(f"\n{continue_prompt}")
    return config
