"""
交互式配置向导模块
"""

import os
import sys
import shutil
from viby.locale import get_text, init_text_manager
from viby.utils.formatting import print_separator
from viby.config.app_config import ModelProfileConfig

PASS_SENTINEL = "_viby_internal_pass_"

def print_header(title):
    """打印配置向导标题"""
    print()
    print_separator("=")
    print(f"{title:^{shutil.get_terminal_size().columns}}")
    print_separator("=")
    print()


def get_input(prompt, default=None, validator=None, choices=None, allow_pass_keyword=False):
    """获取用户输入，支持默认值和验证"""
    base_prompt_text = prompt
    if allow_pass_keyword:
        pass_hint = get_text("CONFIG_WIZARD", "PASS_PROMPT_HINT")
        base_prompt_text = f"{prompt} {pass_hint}"
            
    if default is not None:
        prompt_text = f"{base_prompt_text} [{default}]: "
    else:
        prompt_text = f"{base_prompt_text}: "
    
    while True:
        user_input = input(prompt_text).strip()

        if allow_pass_keyword and user_input.lower() == "pass":
            return PASS_SENTINEL
        
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
    """配置向导主函数"""
    # 初始化文本管理器，加载初始语言文本
    init_text_manager(config)
    
    # 检查当前终端是否支持中文
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
    else:
        config.language = "en-US"
    init_text_manager(config)
    print("\n" + get_text("CONFIG_WIZARD", "selected_language"))
        
    temp_prompt = get_text("CONFIG_WIZARD", "temperature_prompt")
    max_tokens_prompt = get_text("CONFIG_WIZARD", "max_tokens_prompt")
    api_timeout_prompt = get_text("CONFIG_WIZARD", "api_timeout_prompt")
    save_prompt = get_text("CONFIG_WIZARD", "config_saved")
    continue_prompt = get_text("CONFIG_WIZARD", "continue_prompt")
    
    print()
    print_separator()

    # --- 全局API设置 --- 
    default_api_url_prompt = get_text("CONFIG_WIZARD", "default_api_url_prompt") if callable(get_text) else "默认API基地址"
    config.default_api_base_url = get_input(default_api_url_prompt, config.default_api_base_url or "http://localhost:11434", validator=validate_url)
    
    default_api_key_prompt = get_text("CONFIG_WIZARD", "default_api_key_prompt") if callable(get_text) else "默认API密钥（可选）"
    config.default_api_key = get_input(default_api_key_prompt, config.default_api_key or "", allow_pass_keyword=True)
    if not config.default_api_key or config.default_api_key == PASS_SENTINEL: 
        config.default_api_key = None

    print_separator()

    # --- 默认模型配置（必填） ---
    print_header(get_text("CONFIG_WIZARD", "default_model_header"))
    
    # 确保default_model是ModelProfileConfig实例并且有一个名称。
    # 这应该是由app_config.py的初始化保证的，但作为一个安全措施：
    if not isinstance(config.default_model, ModelProfileConfig):
        config.default_model = ModelProfileConfig(name="qwen3:30b") 
    elif not config.default_model.name:
        config.default_model.name = "qwen3:30b"

    default_model_name_prompt_text = get_text("CONFIG_WIZARD", "default_model_name_prompt")
    # 直接获取模型名称输入，使用现有名称作为默认值。
    config.default_model.name = get_input(default_model_name_prompt_text, config.default_model.name)

    # 格式化提示字符串以包含实际模型名称
    formatted_default_model_url_prompt = get_text("CONFIG_WIZARD", "model_specific_url_prompt").format(model_name=config.default_model.name)
    user_provided_default_model_url = get_input(
        formatted_default_model_url_prompt, 
        config.default_model.api_base_url or "", 
        validator=lambda x: not x or validate_url(x), 
        allow_pass_keyword=True
    )
    if not user_provided_default_model_url or user_provided_default_model_url == PASS_SENTINEL:
        config.default_model.api_base_url = None  # 存储None以使用全局
    else:
        config.default_model.api_base_url = user_provided_default_model_url
        
    # 格式化提示字符串以包含实际模型名称
    formatted_default_model_key_prompt = get_text("CONFIG_WIZARD", "model_specific_key_prompt").format(model_name=config.default_model.name)
    config.default_model.api_key = get_input(formatted_default_model_key_prompt, config.default_model.api_key or "", allow_pass_keyword=True)
    if not config.default_model.api_key or config.default_model.api_key == PASS_SENTINEL:
        config.default_model.api_key = None  # 存储None如果为空

    print_separator()

    # --- 思考模型配置（可选） ---
    print_header(get_text("CONFIG_WIZARD", "think_model_header"))
    think_model_name_prompt = get_text("CONFIG_WIZARD", "think_model_name_prompt")
    current_think_model_name = config.think_model.name if config.think_model else ""
    
    think_model_name_input = get_input(think_model_name_prompt, current_think_model_name, allow_pass_keyword=True)

    if think_model_name_input and think_model_name_input != PASS_SENTINEL:
        if not config.think_model or config.think_model.name != think_model_name_input:
            config.think_model = ModelProfileConfig(name=think_model_name_input)
        # 如果名称没有改变并且配置文件存在，我们只需在下面确认/更新URL/密钥
        
        # 格式化提示字符串以包含实际模型名称
        formatted_think_model_url_prompt = get_text("CONFIG_WIZARD", "model_specific_url_prompt").format(model_name=config.think_model.name)
        user_provided_think_model_url = get_input(
            formatted_think_model_url_prompt, 
            config.think_model.api_base_url or "", 
            validator=lambda x: not x or validate_url(x),
            allow_pass_keyword=True
        )
        if not user_provided_think_model_url or user_provided_think_model_url == PASS_SENTINEL:
            config.think_model.api_base_url = None
        else:
            config.think_model.api_base_url = user_provided_think_model_url

        # 格式化提示字符串以包含实际模型名称
        formatted_think_model_key_prompt = get_text("CONFIG_WIZARD", "model_specific_key_prompt").format(model_name=config.think_model.name)
        config.think_model.api_key = get_input(formatted_think_model_key_prompt, config.think_model.api_key or "", allow_pass_keyword=True)
        if not config.think_model.api_key or config.think_model.api_key == PASS_SENTINEL:
            config.think_model.api_key = None
    elif config.think_model: # 用户输入“pass”或空白名称
        config.think_model = None 

    print_separator()

    # --- 快速模型配置（可选） ---
    print_header(get_text("CONFIG_WIZARD", "fast_model_header"))
    fast_model_name_prompt = get_text("CONFIG_WIZARD", "fast_model_name_prompt")
    current_fast_model_name = config.fast_model.name if config.fast_model else ""

    fast_model_name_input = get_input(fast_model_name_prompt, current_fast_model_name, allow_pass_keyword=True)

    if fast_model_name_input and fast_model_name_input != PASS_SENTINEL:
        if not config.fast_model or config.fast_model.name != fast_model_name_input:
            config.fast_model = ModelProfileConfig(name=fast_model_name_input)
        
        # 格式化提示字符串以包含实际模型名称
        formatted_fast_model_url_prompt = get_text("CONFIG_WIZARD", "model_specific_url_prompt").format(model_name=config.fast_model.name)
        user_provided_fast_model_url = get_input(
            formatted_fast_model_url_prompt, 
            config.fast_model.api_base_url or "", 
            validator=lambda x: not x or validate_url(x),
            allow_pass_keyword=True
        )
        if not user_provided_fast_model_url or user_provided_fast_model_url == PASS_SENTINEL:
            config.fast_model.api_base_url = None
        else:
            config.fast_model.api_base_url = user_provided_fast_model_url
        
        # 格式化提示字符串以包含实际模型名称
        formatted_fast_model_key_prompt = get_text("CONFIG_WIZARD", "model_specific_key_prompt").format(model_name=config.fast_model.name)
        config.fast_model.api_key = get_input(formatted_fast_model_key_prompt, config.fast_model.api_key or "", allow_pass_keyword=True)
        if not config.fast_model.api_key or config.fast_model.api_key == PASS_SENTINEL:
            config.fast_model.api_key = None
    elif config.fast_model: # 用户输入“pass”或空白名称
        config.fast_model = None 

    print_separator()

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
    
    
    # API超时
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
    
    # MCP工具设置
    enable_mcp_prompt = get_text("CONFIG_WIZARD", "enable_mcp_prompt")
    enable_mcp_choices = [get_text("CONFIG_WIZARD", "yes"), get_text("CONFIG_WIZARD", "no")]
    enable_mcp = number_choice(enable_mcp_choices, enable_mcp_prompt)
    config.enable_mcp = (enable_mcp == get_text("CONFIG_WIZARD", "yes"))
    
    # 如果启用了MCP，显示配置文件夹信息
    if config.enable_mcp:
        print("\n" + get_text("CONFIG_WIZARD", "mcp_config_info").format(config.config_dir))
    
    # 保存配置
    config.save_config()
    
    print()
    print_separator()
    print(f"{save_prompt}: {config.config_path}")
    input(f"\n{continue_prompt}")
    return config
