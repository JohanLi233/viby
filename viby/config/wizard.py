"""
交互式配置向导模块
"""

import os
import sys
from viby.locale import get_text, init_text_manager
from viby.utils.ui import (
    print_header,
    print_separator,
    get_input,
    number_choice,
    show_error,
    show_warning,
    show_success,
    show_info,
    console,
)
from viby.config.app_config import ModelProfileConfig

# 用于表示用户选择跳过某项配置的内部标记
PASS_SENTINEL = "_viby_internal_pass_"


def validate_url(url):
    """验证URL格式"""
    if not url.startswith(("http://", "https://")):
        show_error(get_text("CONFIG_WIZARD", "url_error"))
        return False
    return True


def configure_model_profile(profile, model_type, config):
    """配置模型资料"""
    model_name_prompt = get_text("CONFIG_WIZARD", f"{model_type}_model_name_prompt")
    current_name = profile.name if profile else ""

    name_input = get_input(model_name_prompt, current_name, allow_pass_keyword=True)

    if not name_input or name_input == PASS_SENTINEL:
        return None

    if not profile or profile.name != name_input:
        profile = ModelProfileConfig(name=name_input)

    # 模型特定URL
    url_prompt = get_text("CONFIG_WIZARD", "model_specific_url_prompt").format(
        model_name=profile.name
    )
    url_input = get_input(
        url_prompt,
        profile.api_base_url or "",
        validator=lambda x: not x or validate_url(x),
        allow_pass_keyword=True,
    )
    profile.api_base_url = (
        None if not url_input or url_input == PASS_SENTINEL else url_input
    )

    # 模型特定API密钥
    key_prompt = get_text("CONFIG_WIZARD", "model_specific_key_prompt").format(
        model_name=profile.name
    )
    key_input = get_input(key_prompt, profile.api_key or "", allow_pass_keyword=True)
    profile.api_key = None if not key_input or key_input == PASS_SENTINEL else key_input

    # 最大令牌数
    tokens_prompt = get_text("CONFIG_WIZARD", "model_max_tokens_prompt").format(
        model_name=profile.name
    )
    while True:
        max_tokens = get_input(tokens_prompt, str(profile.max_tokens or 40960))
        try:
            tokens_value = int(max_tokens)
            if tokens_value > 0:
                profile.max_tokens = tokens_value
                break
            show_warning(get_text("CONFIG_WIZARD", "tokens_positive"))
        except ValueError:
            show_error(get_text("CONFIG_WIZARD", "invalid_integer"))

    # 温度设置
    temp_prompt = get_text("CONFIG_WIZARD", "model_temperature_prompt").format(
        model_name=profile.name
    )
    while True:
        temperature = get_input(
            temp_prompt, str(profile.temperature or 0.7), allow_pass_keyword=True
        )
        if temperature == PASS_SENTINEL:
            profile.temperature = None
            break
        try:
            temp_value = float(temperature)
            if 0.0 <= temp_value <= 1.0:
                profile.temperature = temp_value
                break
            show_warning(get_text("CONFIG_WIZARD", "temperature_range"))
        except ValueError:
            show_error(get_text("CONFIG_WIZARD", "invalid_decimal"))

    # top_p设置
    top_p_prompt = get_text("CONFIG_WIZARD", "model_top_p_prompt").format(
        model_name=profile.name
    )
    top_p = get_input(top_p_prompt, str(profile.top_p or ""), allow_pass_keyword=True)
    if top_p == PASS_SENTINEL or not top_p:
        profile.top_p = None
    else:
        try:
            top_p_value = float(top_p)
            if 0.0 <= top_p_value <= 1.0:
                profile.top_p = top_p_value
            else:
                show_warning(get_text("CONFIG_WIZARD", "top_p_range"))
                profile.top_p = None
        except ValueError:
            show_error(get_text("CONFIG_WIZARD", "invalid_top_p"))
            profile.top_p = None

    return profile


def configure_embedding_model(config):
    """配置嵌入模型"""
    # 显示嵌入模型配置标题
    console.print()
    print_header(get_text("CONFIG_WIZARD", "embedding_model_header"))

    # 嵌入模型名称
    model_prompt = get_text("CONFIG_WIZARD", "embedding_model_name_prompt")
    model_name = get_input(model_prompt, config.embedding.model_name)
    config.embedding.model_name = model_name

    return config


def run_config_wizard(config):
    """配置向导主函数"""
    # 初始化文本管理器，加载初始语言文本
    init_text_manager(config)

    # 检查当前终端是否支持中文
    is_chinese_supported = True
    try:
        show_info(get_text("CONFIG_WIZARD", "checking_chinese"))
        sys.stdout.write("测试中文支持\n")
        sys.stdout.flush()
    except UnicodeEncodeError:
        is_chinese_supported = False

    # 清屏
    os.system("cls" if os.name == "nt" else "clear")

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
    console.print("\n" + get_text("CONFIG_WIZARD", "selected_language"))

    console.print()
    print_separator()

    # --- 默认模型配置 ---
    print_header(get_text("CONFIG_WIZARD", "default_model_header"))
    config.default_model = configure_model_profile(
        config.default_model, "default", config
    )
    print_separator()

    # --- 思考模型配置 ---
    print_header(get_text("CONFIG_WIZARD", "think_model_header"))
    config.think_model = configure_model_profile(config.think_model, "think", config)
    print_separator()

    # --- 快速模型配置 ---
    print_header(get_text("CONFIG_WIZARD", "fast_model_header"))
    config.fast_model = configure_model_profile(config.fast_model, "fast", config)
    print_separator()

    # --- 嵌入模型配置 ---
    print_header(get_text("CONFIG_WIZARD", "embedding_model_header", "嵌入模型配置"))
    config = configure_embedding_model(config)
    print_separator()

    # --- 自动压缩配置 ---
    print_header(get_text("CONFIG_WIZARD", "autocompact_header", "消息自动压缩配置"))

    # 启用/禁用自动压缩
    enable_autocompact_prompt = get_text(
        "CONFIG_WIZARD", "enable_autocompact_prompt", "启用消息自动压缩功能"
    )
    enable_autocompact_choices = [
        get_text("CONFIG_WIZARD", "yes"),
        get_text("CONFIG_WIZARD", "no"),
    ]
    enable_autocompact = number_choice(
        enable_autocompact_choices, enable_autocompact_prompt
    )
    config.autocompact.enabled = enable_autocompact == get_text("CONFIG_WIZARD", "yes")

    if config.autocompact.enabled:
        # 配置压缩阈值
        threshold_prompt = get_text(
            "CONFIG_WIZARD",
            "autocompact_threshold_prompt",
            "压缩阈值 (当消息token数量超过max_tokens的比例时触发压缩, 0.1-0.9)",
        )
        while True:
            threshold = get_input(
                threshold_prompt, str(config.autocompact.threshold_ratio)
            )
            try:
                threshold_value = float(threshold)
                if 0.1 <= threshold_value <= 0.9:
                    config.autocompact.threshold_ratio = threshold_value
                    break
                show_warning(
                    get_text(
                        "CONFIG_WIZARD", "threshold_range", "阈值必须在0.1和0.9之间!"
                    )
                )
            except ValueError:
                show_error(get_text("CONFIG_WIZARD", "invalid_decimal"))

        # 配置保留对话轮数
        keep_exchanges_prompt = get_text(
            "CONFIG_WIZARD", "keep_exchanges_prompt", "保留最近几轮对话不压缩 (1-5)"
        )
        while True:
            keep_exchanges = get_input(
                keep_exchanges_prompt, str(config.autocompact.keep_last_exchanges)
            )
            try:
                keep_value = int(keep_exchanges)
                if 1 <= keep_value <= 5:
                    config.autocompact.keep_last_exchanges = keep_value
                    break
                show_warning(
                    get_text(
                        "CONFIG_WIZARD",
                        "keep_exchanges_range",
                        "保留轮数必须在1和5之间!",
                    )
                )
            except ValueError:
                show_error(get_text("CONFIG_WIZARD", "invalid_integer"))

    print_separator()

    # MCP工具设置
    enable_mcp_prompt = get_text("CONFIG_WIZARD", "enable_mcp_prompt")
    enable_mcp_choices = [
        get_text("CONFIG_WIZARD", "yes"),
        get_text("CONFIG_WIZARD", "no"),
    ]
    enable_mcp = number_choice(enable_mcp_choices, enable_mcp_prompt)
    config.enable_mcp = enable_mcp == get_text("CONFIG_WIZARD", "yes")

    # 如果启用了MCP，显示配置文件夹信息
    if config.enable_mcp:
        show_info(
            "\n"
            + get_text("CONFIG_WIZARD", "mcp_config_info").format(config.config_dir)
        )

        # 工具搜索设置
        enable_tool_search_prompt = get_text(
            "CONFIG_WIZARD",
            "enable_tool_search_prompt",
            "启用MCP工具搜索功能（根据查询智能选择相关工具）",
        )
        enable_tool_search_choices = [
            get_text("CONFIG_WIZARD", "yes"),
            get_text("CONFIG_WIZARD", "no"),
        ]
        enable_tool_search = number_choice(
            enable_tool_search_choices, enable_tool_search_prompt
        )
        config.enable_tool_search = enable_tool_search == get_text(
            "CONFIG_WIZARD", "yes"
        )

    # Yolo模式设置
    enable_yolo_prompt = get_text("CONFIG_WIZARD", "enable_yolo_mode_prompt")
    enable_yolo_choices = [
        get_text("CONFIG_WIZARD", "no"),
        get_text("CONFIG_WIZARD", "yes"),
    ]
    enable_yolo = number_choice(enable_yolo_choices, enable_yolo_prompt)
    config.enable_yolo_mode = enable_yolo == get_text("CONFIG_WIZARD", "yes")

    # 保存配置
    config.save_config()

    console.print()
    print_separator()
    show_success(f"{get_text('CONFIG_WIZARD', 'config_saved')}: {config.config_path}")
    get_input(f"\n{get_text('CONFIG_WIZARD', 'continue_prompt')}", default="")
    return config
